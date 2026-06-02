"""Test Fase 3d — Reports, Market via yfinance (mock), integrasi erosi di transaksi."""
import time
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


def _auth(client, email, password="pass", name="U"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


def _setup_wallet_cat(client):
    wid = client.post("/api/wallets", json={"name": "W", "type": "cash"}).get_json()["data"]["id"]
    cid = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
    cid2 = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
    return wid, cid, cid2


def _mock_ticker_close(close_value, dates=None):
    """Buat mock yf.Ticker yang mengembalikan DataFrame dengan satu baris Close."""
    if dates is None:
        dates = ["2026-05-30"]
    mock = MagicMock()
    mock.history.return_value = pd.DataFrame(
        {"Close": [close_value] * len(dates)},
        index=pd.to_datetime(dates),
    )
    return mock


def _mock_ticker_history(close_values, dates):
    """Buat mock yf.Ticker untuk riwayat multi-tanggal."""
    mock = MagicMock()
    mock.history.return_value = pd.DataFrame(
        {"Close": close_values},
        index=pd.to_datetime(dates),
    )
    return mock


# ============================================================
# REPORT SERVICE
# ============================================================
class TestReportService:
    def test_summary_akurat(self, client):
        _auth(client, "rsum@test.com")
        wid, cid, cid2 = _setup_wallet_cat(client)
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 5_000_000, "kind": "income", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2,
                                               "amount": 1_000_000, "kind": "expense", "date": "2026-05-10"})
        resp = client.get("/api/reports/summary?month=5&year=2026")
        data = resp.get_json()["data"]
        assert data["income"] == 5_000_000
        assert data["expense"] == 1_000_000
        assert data["selisih"] == 4_000_000

    def test_by_category(self, client):
        _auth(client, "rcat@test.com")
        wid, cid, cid2 = _setup_wallet_cat(client)
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2,
                                               "amount": 300_000, "kind": "expense", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2,
                                               "amount": 200_000, "kind": "expense", "date": "2026-05-15"})
        resp = client.get("/api/reports/by-category?month=5&year=2026")
        data = resp.get_json()["data"]
        assert len(data) == 1
        assert data[0]["total"] == 500_000

    def test_trend_panjang(self, client):
        _auth(client, "rtrend@test.com")
        resp = client.get("/api/reports/trend?months=6")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 6

    def test_trend_harian_mode_bulan(self, client):
        """Tren harian mode ?month=&year= → satu titik per hari di bulan itu."""
        _auth(client, "rdaily1@test.com")
        wid, cid, cid2 = _setup_wallet_cat(client)
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 500_000, "kind": "income", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2,
                                               "amount": 75_000, "kind": "expense", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2,
                                               "amount": 25_000, "kind": "expense", "date": "2026-05-03"})
        resp = client.get("/api/reports/trend-daily?month=5&year=2026")
        assert resp.status_code == 200
        body = resp.get_json()
        data = body["data"]
        # Mei punya 31 hari → 31 titik (hari kosong terisi 0)
        assert len(data) == 31
        assert len(body["chart"]["labels"]) == 31
        # Hari pertama: income 500rb, expense 75rb digabung
        h1 = next(d for d in data if d["date"] == "2026-05-01")
        assert h1["income"] == 500_000
        assert h1["expense"] == 75_000
        # Hari tanpa transaksi → 0
        h2 = next(d for d in data if d["date"] == "2026-05-02")
        assert h2["income"] == 0 and h2["expense"] == 0
        # Total harian == total bulan
        assert sum(d["income"] for d in data) == 500_000
        assert sum(d["expense"] for d in data) == 100_000

    def test_trend_harian_mode_days_dibatasi(self, client):
        """Mode ?days=N dibatasi maksimal 186 hari (~6 bulan) untuk pilihan 30h/3bln/6bln."""
        _auth(client, "rdaily2@test.com")
        resp = client.get("/api/reports/trend-daily?days=999")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 186  # di-clamp ke maksimal ~6 bulan


# ============================================================
# MARKET SERVICE — mock yfinance (tidak butuh koneksi internet)
# ============================================================
class TestMarketAPI:
    def test_usd_idr_sukses(self, client):
        """Kurs USD/IDR berhasil diambil dari yfinance."""
        _auth(client, "musd@test.com")
        from app.services import market_service
        market_service.reset_cache()

        mock = _mock_ticker_close(16_000.0)
        with patch("app.services.market_service.yf.Ticker", return_value=mock):
            resp = client.get("/api/market/usd-idr")

        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["rate"] == 16_000.0
        assert data["source"] == "yfinance"

    def test_usd_idr_api_gagal_fallback(self, client):
        """Bila yfinance gagal, harus fallback ke cache terakhir — bukan crash."""
        _auth(client, "mfallback@test.com")
        from app.services import market_service
        market_service.reset_cache()

        # Isi cache terlebih dahulu dengan data valid, lalu buat TTL habis
        market_service._cache["usd_idr"] = {
            "data": {"rate": 15_500.0, "source": "yfinance", "cached": False},
            "ts": 0,  # TTL habis
        }

        with patch("app.services.market_service.yf.Ticker", side_effect=Exception("Timeout!")):
            resp = client.get("/api/market/usd-idr")

        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["rate"] == 15_500.0
        assert data["source"] == "fallback"

    def test_usd_idr_tanpa_cache_unavailable(self, client):
        """Bila yfinance gagal dan tidak ada cache → rate: null, tidak crash."""
        _auth(client, "mnodata@test.com")
        from app.services import market_service
        market_service.reset_cache()

        with patch("app.services.market_service.yf.Ticker", side_effect=Exception("Timeout!")):
            resp = client.get("/api/market/usd-idr")

        assert resp.status_code == 200
        assert resp.get_json()["data"]["rate"] is None

    def test_gold_sukses(self, client):
        """Harga emas berhasil diambil dan dikonversi ke IDR."""
        _auth(client, "mgold@test.com")
        from app.services import market_service
        market_service.reset_cache()

        # IDR=X → 16.000, GC=F → 3.200 USD/oz → 3.200 × 16.000 = 51.200.000 IDR/oz
        def _ticker_factory(symbol):
            if symbol == "IDR=X":
                return _mock_ticker_close(16_000.0)
            return _mock_ticker_close(3_200.0)

        with patch("app.services.market_service.yf.Ticker", side_effect=_ticker_factory):
            resp = client.get("/api/market/gold")

        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["price_idr"] is not None
        assert data["price_idr"] == 3_200 * 16_000


# ============================================================
# MARKET HISTORY — endpoint GET /api/market/usd-idr/history
# ============================================================
class TestMarketHistory:
    def test_history_sukses(self, client):
        """Endpoint history mengembalikan daftar tanggal-rate yang benar."""
        _auth(client, "mhist@test.com")
        from app.services import market_service
        market_service.reset_cache()

        dates = ["2026-05-01", "2026-05-02", "2026-05-03"]
        values = [15_800.0, 15_900.0, 16_000.0]
        mock = _mock_ticker_history(values, dates)

        with patch("app.services.market_service.yf.Ticker", return_value=mock):
            resp = client.get("/api/market/usd-idr/history?months=6")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        data = body["data"]
        assert len(data) == 3
        assert data[0]["date"] == "2026-05-01"
        assert data[0]["rate"] == 15_800.0
        assert data[-1]["date"] == "2026-05-03"

    def test_history_gagal_kembalikan_list_kosong(self, client):
        """Bila yfinance gagal, history mengembalikan [] — tidak crash."""
        _auth(client, "mhistfail@test.com")
        from app.services import market_service
        market_service.reset_cache()

        with patch("app.services.market_service.yf.Ticker", side_effect=Exception("Down!")):
            resp = client.get("/api/market/usd-idr/history")

        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_history_default_months(self, client):
        """Tanpa parameter months, default 6 bulan tetap jalan."""
        _auth(client, "mhistdef@test.com")
        from app.services import market_service
        market_service.reset_cache()

        mock = _mock_ticker_history([16_000.0], ["2026-05-30"])
        with patch("app.services.market_service.yf.Ticker", return_value=mock):
            resp = client.get("/api/market/usd-idr/history")

        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True


# ============================================================
# EROSI DI TRANSAKSI API
# ============================================================
class TestErosiDiTransaksi:
    def test_income_punya_field_erosi(self, client):
        """Transaksi income harus selalu memiliki field erosi di respons GET."""
        _auth(client, "erosi1@test.com")
        from app.services import market_service
        market_service.reset_cache()
        wid, cid, _ = _setup_wallet_cat(client)

        # Kurs disimpan berdasarkan TANGGAL transaksi (historis) → patch _kurs_pada_tanggal
        with patch("app.api.transactions._kurs_pada_tanggal", return_value=16_000.0):
            client.post("/api/transactions", json={
                "wallet_id": wid, "category_id": cid,
                "amount": 5_000_000, "kind": "income", "date": "2026-05-01"
            })

        with patch("app.api.transactions._kurs_sekarang", return_value=16_000.0):
            resp = client.get("/api/transactions")

        trxs = resp.get_json()["data"]
        income = next(t for t in trxs if t["kind"] == "income")
        assert "erosi" in income

    def test_income_erosi_akurat(self, client):
        """Erosi 15.000→16.000 harus ≈ 6,25%."""
        _auth(client, "erosi2@test.com")
        from app.services import market_service
        market_service.reset_cache()
        wid, cid, _ = _setup_wallet_cat(client)

        # Kurs SAAT transaksi (historis) = 15.000 → patch _kurs_pada_tanggal
        with patch("app.api.transactions._kurs_pada_tanggal", return_value=15_000.0):
            client.post("/api/transactions", json={
                "wallet_id": wid, "category_id": cid,
                "amount": 5_000_000, "kind": "income", "date": "2026-05-01"
            })

        # Kurs sekarang = 16.000 → erosi (15.000 → 16.000) ≈ 6,25%
        with patch("app.api.transactions._kurs_sekarang", return_value=16_000.0):
            resp = client.get("/api/transactions")

        trxs = resp.get_json()["data"]
        income = next(t for t in trxs if t["kind"] == "income")
        erosi = income["erosi"]
        assert erosi is not None
        assert abs(erosi["erosi_persen"] - 6.25) < 0.01
        # Kurs awal & sekarang ikut dilampirkan untuk tooltip frontend
        assert erosi["usd_rate_at_date"] == 15_000.0
        assert erosi["usd_rate_sekarang"] == 16_000.0

    def test_income_tanpa_kurs_erosi_none(self, client):
        """Income tanpa usd_rate_at_date → erosi: null, tidak crash."""
        _auth(client, "erosi3@test.com")
        from app.services import market_service
        market_service.reset_cache()
        wid, cid, _ = _setup_wallet_cat(client)

        with patch("app.api.transactions._kurs_pada_tanggal", return_value=None):
            client.post("/api/transactions", json={
                "wallet_id": wid, "category_id": cid,
                "amount": 5_000_000, "kind": "income", "date": "2026-05-01"
            })

        with patch("app.api.transactions._kurs_sekarang", return_value=None):
            resp = client.get("/api/transactions")

        trxs = resp.get_json()["data"]
        income = next(t for t in trxs if t["kind"] == "income")
        assert income["erosi"] is None

    def test_income_pakai_kurs_historis_tanggal(self, client):
        """Kurs yang disimpan harus kurs PADA TANGGAL transaksi (historis), bukan hari ini."""
        _auth(client, "erosi4@test.com")
        from app.services import market_service
        market_service.reset_cache()
        wid, cid, _ = _setup_wallet_cat(client)

        # Simulasikan market_service mengembalikan kurs berbeda sesuai tanggal
        def kurs_palsu(tgl):
            return 14_000.0 if tgl.isoformat() == "2026-01-15" else 16_000.0

        with patch("app.services.market_service.get_usd_idr_at_date", side_effect=kurs_palsu):
            client.post("/api/transactions", json={
                "wallet_id": wid, "category_id": cid,
                "amount": 5_000_000, "kind": "income", "date": "2026-01-15"
            })

        resp = client.get("/api/transactions")
        income = next(t for t in resp.get_json()["data"] if t["kind"] == "income")
        # Kurs tersimpan harus 14.000 (kurs historis 15 Jan), bukan 16.000 (hari ini)
        assert income["usd_rate_at_date"] == 14_000.0
