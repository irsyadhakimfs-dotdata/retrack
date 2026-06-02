"""Test Perubahan 4 — Data Warehouse: ETL, API query DWH."""
import pytest
from unittest.mock import patch
from app.models.dwh import FactTransaction


# -------------------------------------------------------
# Helper: register + login
# -------------------------------------------------------
def _auth(client, email, password="pass", name="U"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login",    json={"email": email, "password": password})


def _setup_transaksi(client):
    """Buat wallet, kategori, dan beberapa transaksi. Kembalikan (wid, cid_inc, cid_exp)."""
    wid   = client.post("/api/wallets",    json={"name": "DWH-W", "type": "bank"}).get_json()["data"]["id"]
    c_inc = client.post("/api/categories", json={"name": "Gaji",  "kind": "income"}).get_json()["data"]["id"]
    c_exp = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]

    # Transaksi income dengan kurs (untuk erosi)
    client.post("/api/transactions", json={
        "wallet_id": wid, "category_id": c_inc,
        "amount": 5_000_000, "kind": "income",
        "date": "2026-04-01", "usd_rate_at_date": 16000.0,
    })
    # Transaksi expense
    client.post("/api/transactions", json={
        "wallet_id": wid, "category_id": c_exp,
        "amount": 1_200_000, "kind": "expense",
        "date": "2026-04-15",
    })
    return wid, c_inc, c_exp


class TestEtlRun:
    def test_etl_run_sukses(self, client):
        """POST /api/dwh/etl/run harus berhasil dan mengembalikan stats yang valid."""
        _auth(client, "etl1@test.com")
        _setup_transaksi(client)

        # Mock kurs agar tidak perlu internet
        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=16500.0):
            resp = client.post("/api/dwh/etl/run")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        stats = body["data"]
        assert "loaded"  in stats
        assert "skipped" in stats
        assert "errors"  in stats
        assert stats["loaded"] >= 0

    def test_etl_tanpa_transaksi(self, client):
        """ETL pada akun kosong harus tetap berhasil dengan loaded=0."""
        _auth(client, "etl_empty@test.com")

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=None):
            resp = client.post("/api/dwh/etl/run")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        assert body["data"]["loaded"] == 0

    def test_etl_idempoten(self, client):
        """Menjalankan ETL dua kali tidak boleh menambah baris FactTransaction."""
        _auth(client, "etl2@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=16500.0):
            resp1 = client.post("/api/dwh/etl/run")
            stats1 = resp1.get_json()["data"]

            resp2 = client.post("/api/dwh/etl/run")
            stats2 = resp2.get_json()["data"]

        # Baris yang dimuat pada run pertama harus menjadi "skipped" pada run kedua
        assert stats1["loaded"] == stats2["skipped"]
        # Run kedua tidak boleh menambah baris baru
        assert stats2["loaded"] == 0

    def test_etl_butuh_login(self, client):
        """ETL tanpa login harus ditolak (redirect atau 401)."""
        resp = client.post("/api/dwh/etl/run")
        # Flask-Login redirect ke halaman login (302) atau bisa 401
        assert resp.status_code in (302, 401)


class TestDwhSummary:
    def test_summary_struktur_benar(self, client):
        """GET /api/dwh/summary harus mengembalikan list dengan kunci month/income/expense."""
        _auth(client, "sum1@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=16500.0):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/summary?year=2026")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        data = body["data"]
        assert isinstance(data, list)

        if data:
            item = data[0]
            assert "month"      in item
            assert "month_name" in item
            assert "income"     in item
            assert "expense"    in item

    def test_summary_nilai_benar(self, client):
        """Summary harus mencerminkan total transaksi yang sudah di-ETL."""
        _auth(client, "sum2@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=None):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/summary?year=2026")
        data = resp.get_json()["data"]

        # Cari bulan April (month=4)
        april = next((d for d in data if d["month"] == 4), None)
        assert april is not None
        assert april["income"]  == 5_000_000.0
        assert april["expense"] == 1_200_000.0


class TestTopCategories:
    def test_top_categories_adalah_list(self, client):
        """GET /api/dwh/top-categories harus mengembalikan list."""
        _auth(client, "topcat1@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=None):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/top-categories?months=3&kind=expense")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        assert isinstance(body["data"], list)

    def test_top_categories_struktur(self, client):
        """Setiap item top-categories harus punya kunci category/total/count."""
        _auth(client, "topcat2@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=None):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/top-categories?months=3&kind=expense")
        data = resp.get_json()["data"]

        if data:
            assert "category" in data[0]
            assert "total"    in data[0]
            assert "count"    in data[0]


class TestErosiSummary:
    def test_erosi_summary_struktur(self, client):
        """GET /api/dwh/erosi-summary harus mengembalikan avg_erosi_persen dan total."""
        _auth(client, "erosi1@test.com")
        _setup_transaksi(client)

        # Mock kurs agar erosi_persen terhitung
        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=16500.0):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/erosi-summary")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        d = body["data"]
        assert "avg_erosi_persen"          in d
        assert "total_income_transactions" in d

    def test_erosi_dihitung_bila_kurs_ada(self, client):
        """Bila kurs disuplai saat ETL, avg_erosi_persen tidak boleh None."""
        _auth(client, "erosi2@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=16500.0):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/erosi-summary")
        d = resp.get_json()["data"]
        # Ada 1 transaksi income dengan usd_rate_at_date=16000 dan kurs_sekarang=16500
        assert d["total_income_transactions"] == 1
        assert d["avg_erosi_persen"] is not None

    def test_erosi_kosong_bila_kurs_tidak_ada(self, client):
        """Bila kurs tidak tersedia saat ETL, total transaksi dengan erosi = 0."""
        _auth(client, "erosi3@test.com")
        _setup_transaksi(client)

        with patch("app.services.etl_service._ambil_kurs_sekarang", return_value=None):
            client.post("/api/dwh/etl/run")

        resp = client.get("/api/dwh/erosi-summary")
        d = resp.get_json()["data"]
        # erosi_persen NULL → tidak masuk agregasi → total = 0
        assert d["total_income_transactions"] == 0
        assert d["avg_erosi_persen"] is None
