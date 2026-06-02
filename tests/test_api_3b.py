"""Test Fase 3b — Wallets, Categories, Transactions API."""
import pytest
from datetime import date


# ---------- helper login ----------
def _auth(client, email="u3b@test.com", password="pass123", name="User 3b"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


# ============================================================
# WALLETS
# ============================================================
class TestWalletsAPI:
    def test_list_kosong(self, client):
        _auth(client, "wlist@test.com")
        resp = client.get("/api/wallets")
        assert resp.status_code == 200
        assert resp.get_json()["data"] == []

    def test_create_wallet(self, client):
        _auth(client, "wcreate@test.com")
        resp = client.post("/api/wallets",
                           json={"name": "BCA", "type": "bank", "initial_balance": 500_000})
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["name"] == "BCA"
        assert data["saldo"] == 500_000

    def test_create_wallet_type_invalid(self, client):
        _auth(client, "wtype@test.com")
        resp = client.post("/api/wallets", json={"name": "X", "type": "SALAH"})
        assert resp.status_code == 400

    def test_update_wallet(self, client):
        _auth(client, "wupdate@test.com")
        cid = client.post("/api/wallets", json={"name": "Lama", "type": "cash"}).get_json()["data"]["id"]
        resp = client.put(f"/api/wallets/{cid}", json={"name": "Baru"})
        assert resp.get_json()["data"]["name"] == "Baru"

    def test_delete_wallet_berhasil(self, client):
        _auth(client, "wdel@test.com")
        wid = client.post("/api/wallets", json={"name": "Hapus", "type": "cash"}).get_json()["data"]["id"]
        resp = client.delete(f"/api/wallets/{wid}")
        assert resp.status_code == 200

    def test_delete_wallet_ada_transaksi_ditolak(self, client):
        _auth(client, "wdelt@test.com")
        wid = client.post("/api/wallets", json={"name": "W", "type": "cash"}).get_json()["data"]["id"]
        cid = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
        client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid,
            "amount": 100_000, "kind": "income", "date": "2026-05-01"
        })
        resp = client.delete(f"/api/wallets/{wid}")
        assert resp.status_code == 409

    def test_saldo_terhitung_dari_transaksi(self, client):
        _auth(client, "wsaldo@test.com")
        wid = client.post("/api/wallets", json={"name": "W", "type": "cash",
                                                 "initial_balance": 1_000_000}).get_json()["data"]["id"]
        cid_in = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
        cid_out = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid_in,
                                               "amount": 500_000, "kind": "income", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid_out,
                                               "amount": 200_000, "kind": "expense", "date": "2026-05-02"})
        saldo = client.get("/api/wallets").get_json()["data"][0]["saldo"]
        assert saldo == 1_300_000  # 1_000_000 + 500_000 - 200_000

    def test_wallet_user_lain_tidak_bisa_diakses(self, client):
        _auth(client, "wown1@test.com")
        wid = client.post("/api/wallets", json={"name": "Pribadi", "type": "cash"}).get_json()["data"]["id"]
        # Login sebagai user lain
        client.post("/api/auth/register", json={"email": "wown2@test.com", "password": "x", "name": "B"})
        client.post("/api/auth/login", json={"email": "wown2@test.com", "password": "x"})
        resp = client.put(f"/api/wallets/{wid}", json={"name": "Rampok"})
        assert resp.status_code == 404


# ============================================================
# CATEGORIES
# ============================================================
class TestCategoriesAPI:
    def test_create_dan_list(self, client):
        _auth(client, "clist@test.com")
        client.post("/api/categories", json={"name": "Gaji", "kind": "income"})
        client.post("/api/categories", json={"name": "Makan", "kind": "expense"})
        all_cats = client.get("/api/categories").get_json()["data"]
        assert len(all_cats) == 2

    def test_filter_kind(self, client):
        _auth(client, "cfilt@test.com")
        client.post("/api/categories", json={"name": "Gaji", "kind": "income"})
        client.post("/api/categories", json={"name": "Makan", "kind": "expense"})
        income_cats = client.get("/api/categories?kind=income").get_json()["data"]
        assert all(c["kind"] == "income" for c in income_cats)

    def test_update_dan_delete(self, client):
        _auth(client, "cupd@test.com")
        cid = client.post("/api/categories", json={"name": "Lama", "kind": "expense"}).get_json()["data"]["id"]
        client.put(f"/api/categories/{cid}", json={"name": "Baru"})
        resp = client.get("/api/categories").get_json()["data"]
        assert resp[0]["name"] == "Baru"
        client.delete(f"/api/categories/{cid}")
        assert client.get("/api/categories").get_json()["data"] == []


# ============================================================
# TRANSACTIONS
# ============================================================
class TestTransactionsAPI:
    def _setup(self, client, email):
        _auth(client, email)
        wid = client.post("/api/wallets", json={"name": "W", "type": "cash",
                                                 "initial_balance": 0}).get_json()["data"]["id"]
        cid = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
        cid2 = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
        return wid, cid, cid2

    def test_create_income(self, client):
        wid, cid, _ = self._setup(client, "tin@test.com")
        resp = client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid,
            "amount": 3_000_000, "kind": "income", "date": "2026-05-01"
        })
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["kind"] == "income"
        # Field erosi ada (meski nilainya None karena market_service belum aktif di test)
        assert "erosi" in data

    def test_create_expense(self, client):
        wid, _, cid2 = self._setup(client, "tex@test.com")
        resp = client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid2,
            "amount": 50_000, "kind": "expense", "date": "2026-05-02"
        })
        assert resp.status_code == 201
        assert resp.get_json()["data"]["kind"] == "expense"

    def test_filter_month_year(self, client):
        wid, cid, _ = self._setup(client, "tfilt@test.com")
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 1_000, "kind": "income", "date": "2026-05-01"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 2_000, "kind": "income", "date": "2026-06-01"})
        mei = client.get("/api/transactions?month=5&year=2026").get_json()["data"]
        assert len(mei) == 1
        assert mei[0]["amount"] == 1_000

    def test_filter_keyword(self, client):
        wid, cid, _ = self._setup(client, "tq@test.com")
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 1_000, "kind": "income", "date": "2026-05-01",
                                               "note": "bonus akhir tahun"})
        client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid,
                                               "amount": 2_000, "kind": "income", "date": "2026-05-02",
                                               "note": "gaji bulanan"})
        hasil = client.get("/api/transactions?q=bonus").get_json()["data"]
        assert len(hasil) == 1

    def test_update_transaksi(self, client):
        wid, cid, _ = self._setup(client, "tupd@test.com")
        tid = client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid,
            "amount": 1_000, "kind": "income", "date": "2026-05-01"
        }).get_json()["data"]["id"]
        resp = client.put(f"/api/transactions/{tid}", json={"amount": 9_999})
        assert resp.get_json()["data"]["amount"] == 9_999

    def test_delete_transaksi(self, client):
        wid, cid, _ = self._setup(client, "tdel@test.com")
        tid = client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid,
            "amount": 1_000, "kind": "income", "date": "2026-05-01"
        }).get_json()["data"]["id"]
        resp = client.delete(f"/api/transactions/{tid}")
        assert resp.status_code == 200
        assert client.get("/api/transactions").get_json()["data"] == []

    def test_field_wajib_kosong(self, client):
        _auth(client, "treq@test.com")
        resp = client.post("/api/transactions", json={"amount": 1_000})
        assert resp.status_code == 400
