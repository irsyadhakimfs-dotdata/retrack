"""Test fitur investasi emas — CRUD kepemilikan, ringkasan kenaikan, riwayat harga."""
from unittest.mock import patch


def _auth(client, email, password="pass", name="U"):
    """Helper: daftar + login."""
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


def _buat_emas(client, grams=5, harga=1_000_000, tanggal="2026-01-10"):
    """Helper: buat satu catatan emas, kembalikan response JSON."""
    return client.post("/api/gold", json={
        "grams": grams, "buy_price_per_gram": harga, "date": tanggal,
    })


class TestGoldCrud:
    def test_create_sukses(self, client):
        """POST /api/gold membuat catatan emas dan mengembalikan field yang benar."""
        _auth(client, "gold1@test.com")
        resp = _buat_emas(client, grams=5, harga=1_000_000)
        assert resp.status_code == 201
        d = resp.get_json()["data"]
        assert d["grams"] == 5
        assert d["buy_price_per_gram"] == 1_000_000
        assert d["cost"] == 5_000_000           # 5 gr × 1.000.000
        assert d["buy_date"] == "2026-01-10"
        assert "buy_time" in d                    # waktu masuk dicatat

    def test_create_validasi_field_wajib(self, client):
        """Tanpa grams → 400."""
        _auth(client, "gold2@test.com")
        resp = client.post("/api/gold", json={"buy_price_per_gram": 1_000_000, "date": "2026-01-10"})
        assert resp.status_code == 400

    def test_create_grams_harus_positif(self, client):
        """grams <= 0 → 400."""
        _auth(client, "gold3@test.com")
        resp = _buat_emas(client, grams=0)
        assert resp.status_code == 400

    def test_list_butuh_login(self, client):
        """Tanpa login → 401 (API)."""
        resp = client.get("/api/gold")
        assert resp.status_code == 401

    def test_update_ubah_waktu_masuk(self, client):
        """PUT mengubah tanggal & waktu masuk (fitur 'bisa diedit')."""
        _auth(client, "gold4@test.com")
        hid = _buat_emas(client).get_json()["data"]["id"]
        resp = client.put(f"/api/gold/{hid}", json={"date": "2026-02-20", "time": "09:30"})
        assert resp.status_code == 200
        d = resp.get_json()["data"]
        assert d["buy_date"] == "2026-02-20"
        assert d["buy_time"] == "09:30"

    def test_delete(self, client):
        """DELETE menghapus catatan emas."""
        _auth(client, "gold5@test.com")
        hid = _buat_emas(client).get_json()["data"]["id"]
        assert client.delete(f"/api/gold/{hid}").status_code == 200
        # Setelah dihapus, list kosong
        data = client.get("/api/gold").get_json()["data"]
        assert data["summary"]["count"] == 0

    def test_isolasi_antar_user(self, client):
        """User lain tidak bisa mengubah catatan emas milik user pertama."""
        _auth(client, "gold6a@test.com")
        hid = _buat_emas(client).get_json()["data"]["id"]
        # Login sebagai user berbeda
        _auth(client, "gold6b@test.com")
        assert client.put(f"/api/gold/{hid}", json={"grams": 99}).status_code == 404


class TestGoldSummary:
    def test_kenaikan_dihitung_bila_harga_ada(self, client):
        """Bila harga pasar > harga beli → gain positif dan persen benar."""
        _auth(client, "goldsum1@test.com")
        _buat_emas(client, grams=10, harga=1_000_000)  # modal 10.000.000

        # Harga pasar sekarang 1.200.000/gr → nilai 12.000.000 → gain 2.000.000 (20%)
        with patch("app.api.gold._harga_emas_per_gram_sekarang", return_value=1_200_000):
            data = client.get("/api/gold").get_json()["data"]

        s = data["summary"]
        assert s["total_grams"] == 10
        assert s["total_cost"] == 10_000_000
        assert s["total_value"] == 12_000_000
        assert s["total_gain"] == 2_000_000
        assert abs(s["gain_persen"] - 20.0) < 0.01

    def test_nilai_none_bila_harga_tidak_ada(self, client):
        """Bila harga pasar tidak tersedia → nilai & gain None, tidak crash."""
        _auth(client, "goldsum2@test.com")
        _buat_emas(client, grams=5, harga=1_000_000)

        with patch("app.api.gold._harga_emas_per_gram_sekarang", return_value=None):
            data = client.get("/api/gold").get_json()["data"]

        assert data["summary"]["total_value"] is None
        assert data["summary"]["total_gain"] is None
        assert data["summary"]["total_cost"] == 5_000_000


class TestGoldHistory:
    def test_history_endpoint(self, client):
        """GET /api/market/gold/history mengembalikan list dari service."""
        _auth(client, "goldhist@test.com")
        dummy = [
            {"date": "2026-01-01", "price_idr": 1_000_000},
            {"date": "2026-01-02", "price_idr": 1_010_000},
        ]
        with patch("app.services.market_service.get_gold_history", return_value=dummy):
            resp = client.get("/api/market/gold/history?months=3")

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["ok"] is True
        assert body["data"] == dummy
