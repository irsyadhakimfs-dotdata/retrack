"""Test Fase 3c — Budgets, Goals API + budget_service."""
import pytest
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.category import Category
from app.services.budget_service import hitung_budget


# ---------- helpers ----------
def _auth(client, email, password="pass", name="U"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


# ============================================================
# BUDGET SERVICE (unit test langsung)
# ============================================================
class TestBudgetService:
    def _buat_budget(self, db, sample_user, sample_category_expense, month, year, limit):
        budget = Budget(user_id=sample_user.id, category_id=sample_category_expense.id,
                        month=month, year=year, limit_amount=limit)
        db.session.add(budget)
        db.session.commit()
        return budget

    def _buat_trx(self, db, sample_user, sample_wallet, sample_category_expense, amount, date_str):
        from datetime import date
        trx = Transaction(
            user_id=sample_user.id, wallet_id=sample_wallet.id,
            category_id=sample_category_expense.id, amount=amount,
            kind="expense", date=date.fromisoformat(date_str),
        )
        db.session.add(trx)
        db.session.commit()

    def test_status_aman(self, db, sample_user, sample_wallet, sample_category_expense):
        budget = self._buat_budget(db, sample_user, sample_category_expense, 5, 2026, 2_000_000)
        self._buat_trx(db, sample_user, sample_wallet, sample_category_expense, 500_000, "2026-05-01")
        hasil = hitung_budget(budget)
        assert hasil["status"] == "aman"
        assert hasil["terpakai"] == 500_000
        assert hasil["sisa"] == 1_500_000

    def test_status_hampir(self, db, sample_user, sample_wallet, sample_category_expense):
        budget = self._buat_budget(db, sample_user, sample_category_expense, 6, 2026, 1_000_000)
        self._buat_trx(db, sample_user, sample_wallet, sample_category_expense, 850_000, "2026-06-01")
        hasil = hitung_budget(budget)
        assert hasil["status"] == "hampir"

    def test_status_lewat(self, db, sample_user, sample_wallet, sample_category_expense):
        budget = self._buat_budget(db, sample_user, sample_category_expense, 7, 2026, 500_000)
        self._buat_trx(db, sample_user, sample_wallet, sample_category_expense, 600_000, "2026-07-01")
        hasil = hitung_budget(budget)
        assert hasil["status"] == "lewat"

    def test_limit_nol(self, db, sample_user, sample_wallet, sample_category_expense):
        """Budget limit 0 tidak boleh crash (persen = 0)."""
        budget = self._buat_budget(db, sample_user, sample_category_expense, 8, 2026, 0)
        hasil = hitung_budget(budget)
        assert hasil["persen"] == 0.0


# ============================================================
# BUDGETS API
# ============================================================
class TestBudgetsAPI:
    def _setup(self, client, email):
        _auth(client, email)
        cid = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
        return cid

    def test_create_budget(self, client):
        cid = self._setup(client, "bcreate@test.com")
        resp = client.post("/api/budgets", json={
            "category_id": cid, "month": 5, "year": 2026, "limit_amount": 2_000_000
        })
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["limit_amount"] == 2_000_000
        assert data["status"] == "aman"

    def test_duplikat_ditolak(self, client):
        cid = self._setup(client, "bdup@test.com")
        client.post("/api/budgets", json={"category_id": cid, "month": 5, "year": 2026, "limit_amount": 1_000_000})
        resp = client.post("/api/budgets", json={"category_id": cid, "month": 5, "year": 2026, "limit_amount": 999})
        assert resp.status_code == 409

    def test_filter_bulan(self, client):
        cid = self._setup(client, "bfilt@test.com")
        client.post("/api/budgets", json={"category_id": cid, "month": 5, "year": 2026, "limit_amount": 1_000_000})
        client.post("/api/budgets", json={"category_id": cid, "month": 6, "year": 2026, "limit_amount": 2_000_000})
        hasil = client.get("/api/budgets?month=5&year=2026").get_json()["data"]
        assert len(hasil) == 1

    def test_update_dan_delete(self, client):
        cid = self._setup(client, "bupd@test.com")
        bid = client.post("/api/budgets", json={
            "category_id": cid, "month": 5, "year": 2026, "limit_amount": 1_000_000
        }).get_json()["data"]["id"]
        client.put(f"/api/budgets/{bid}", json={"limit_amount": 3_000_000})
        assert client.get("/api/budgets").get_json()["data"][0]["limit_amount"] == 3_000_000
        client.delete(f"/api/budgets/{bid}")
        assert client.get("/api/budgets").get_json()["data"] == []


# ============================================================
# GOALS API
# ============================================================
class TestGoalsAPI:
    def test_create_goal(self, client):
        _auth(client, "gcreate@test.com")
        resp = client.post("/api/goals", json={
            "name": "Liburan", "target_amount": 5_000_000,
            "saved_amount": 1_000_000, "deadline": "2026-12-31"
        })
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["progress_persen"] == 20.0

    def test_progress_target_nol(self, client):
        """Target 0 tidak boleh crash."""
        _auth(client, "gzero@test.com")
        resp = client.post("/api/goals", json={"name": "Kosong", "target_amount": 0})
        assert resp.status_code == 201
        assert resp.get_json()["data"]["progress_persen"] == 0.0

    def test_estimasi_per_bulan(self, client):
        _auth(client, "gestim@test.com")
        resp = client.post("/api/goals", json={
            "name": "Laptop", "target_amount": 10_000_000,
            "saved_amount": 0, "deadline": "2027-05-01"
        })
        data = resp.get_json()["data"]
        assert data["estimasi_per_bulan"] is not None
        assert data["estimasi_per_bulan"] > 0

    def test_deadline_lewat(self, client):
        """Deadline sudah lewat → estimasi = sisa target (perlu lunas sekarang)."""
        _auth(client, "glewat@test.com")
        resp = client.post("/api/goals", json={
            "name": "Terlambat", "target_amount": 1_000_000,
            "saved_amount": 0, "deadline": "2020-01-01"
        })
        data = resp.get_json()["data"]
        assert data["estimasi_per_bulan"] == 1_000_000

    def test_setor_update_saved(self, client):
        _auth(client, "gsetor@test.com")
        gid = client.post("/api/goals", json={
            "name": "Tabung", "target_amount": 10_000_000, "saved_amount": 0
        }).get_json()["data"]["id"]
        resp = client.put(f"/api/goals/{gid}", json={"saved_amount": 3_000_000})
        assert resp.get_json()["data"]["progress_persen"] == 30.0

    def test_tanpa_deadline_estimasi_none(self, client):
        _auth(client, "gnodl@test.com")
        resp = client.post("/api/goals", json={"name": "Bebas", "target_amount": 5_000_000})
        assert resp.get_json()["data"]["estimasi_per_bulan"] is None

    def test_delete_goal(self, client):
        _auth(client, "gdel@test.com")
        gid = client.post("/api/goals", json={"name": "Hapus", "target_amount": 100_000}).get_json()["data"]["id"]
        resp = client.delete(f"/api/goals/{gid}")
        assert resp.status_code == 200
