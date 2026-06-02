"""Test Fase 5 — Export CSV, User Profile API, Budget nama_kategori, redirect view."""
import pytest


def _auth(client, email="f5@test.com", password="pass123", name="User Fase5"):
    """Helper: register dan login user."""
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


def _setup(client):
    """Buat wallet, kategori income, kategori expense."""
    wid = client.post("/api/wallets", json={"name": "W5", "type": "cash"}).get_json()["data"]["id"]
    cid_in = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
    cid_ex = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
    return wid, cid_in, cid_ex


# ============================================================
# USER PROFILE API
# ============================================================
class TestUserAPI:
    def test_get_me(self, client):
        """GET /api/auth/me harus mengembalikan profil user yang login."""
        _auth(client, "me@test.com")
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["data"]["email"] == "me@test.com"
        assert data["data"]["name"] == "User Fase5"

    def test_get_me_tanpa_login(self, client):
        """GET /api/auth/me tanpa login harus mengembalikan ok: False atau redirect."""
        # Catatan: karena test framework berbagi session, kita cek bahwa
        # endpoint terproteksi tidak memberikan data user orang lain
        # saat diakses tanpa login eksplisit di client ini.
        # Logout dulu untuk memastikan client tidak terautentikasi
        client.post("/api/auth/logout")
        resp = client.get("/api/auth/me")
        # Harus 401 (tidak terautentikasi)
        assert resp.status_code == 401

    def test_put_me_ganti_nama(self, client):
        """PUT /api/auth/me harus mengubah nama pengguna."""
        _auth(client, "putme@test.com")
        resp = client.put("/api/auth/me", json={"name": "Nama Baru"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["data"]["name"] == "Nama Baru"

    def test_put_me_nama_kosong(self, client):
        """PUT /api/auth/me dengan nama kosong harus return 400."""
        _auth(client, "putmekosong@test.com")
        resp = client.put("/api/auth/me", json={"name": ""})
        assert resp.status_code == 400

    def test_ganti_password_berhasil(self, client):
        """PUT /api/auth/password dengan data valid harus berhasil."""
        _auth(client, "pw@test.com", password="lama1234")
        resp = client.put("/api/auth/password", json={
            "current_password": "lama1234",
            "new_password": "baru5678",
        })
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_ganti_password_salah(self, client):
        """PUT /api/auth/password dengan password lama salah harus return 400."""
        _auth(client, "pwsalah@test.com", password="benar123")
        resp = client.put("/api/auth/password", json={
            "current_password": "salah999",
            "new_password": "baru5678",
        })
        assert resp.status_code == 400

    def test_ganti_password_terlalu_pendek(self, client):
        """PUT /api/auth/password dengan password baru < 8 karakter harus return 400."""
        _auth(client, "pwpendek@test.com", password="pass1234")
        resp = client.put("/api/auth/password", json={
            "current_password": "pass1234",
            "new_password": "123",
        })
        assert resp.status_code == 400


# ============================================================
# EXPORT CSV
# ============================================================
class TestExportCSV:
    def test_export_csv_kosong(self, client):
        """GET /api/export/csv tanpa transaksi harus mengembalikan CSV header saja."""
        _auth(client, "csv1@test.com")
        resp = client.get("/api/export/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type
        # Header CSV harus ada di response
        konten = resp.data.decode("utf-8-sig")
        assert "Tanggal" in konten
        assert "Jenis" in konten

    def test_export_csv_dengan_transaksi(self, client):
        """GET /api/export/csv harus mengembalikan baris transaksi."""
        _auth(client, "csv2@test.com")
        wid, cid_in, cid_ex = _setup(client)
        client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid_in,
            "amount": 5_000_000, "kind": "income", "date": "2026-05-01",
            "note": "Gaji Mei",
        })
        client.post("/api/transactions", json={
            "wallet_id": wid, "category_id": cid_ex,
            "amount": 50_000, "kind": "expense", "date": "2026-05-10",
            "note": "Makan siang",
        })
        resp = client.get("/api/export/csv")
        assert resp.status_code == 200
        konten = resp.data.decode("utf-8-sig")
        assert "Gaji Mei" in konten
        assert "Makan siang" in konten
        assert "Pemasukan" in konten
        assert "Pengeluaran" in konten

    def test_export_csv_tanpa_login(self, client):
        """GET /api/export/csv tanpa login harus return 401."""
        # Logout dulu agar client tidak terautentikasi (gunakan view logout yang tidak butuh @login_required)
        client.get("/logout")
        resp = client.get("/api/export/csv")
        assert resp.status_code == 401

    def test_csv_attachment_header(self, client):
        """Response harus memiliki header Content-Disposition attachment."""
        _auth(client, "csv3@test.com")
        resp = client.get("/api/export/csv")
        assert "attachment" in resp.headers.get("Content-Disposition", "")
        assert "refinance-export.csv" in resp.headers.get("Content-Disposition", "")


# ============================================================
# BUDGET DENGAN NAMA KATEGORI
# ============================================================
class TestBudgetNamaKategori:
    def test_budget_ada_nama_kategori(self, client):
        """Response budget harus menyertakan nama_kategori dan persen_terpakai."""
        _auth(client, "budgkat@test.com")
        _, _, cid_ex = _setup(client)
        client.post("/api/budgets", json={
            "category_id": cid_ex, "month": 5, "year": 2026, "limit_amount": 500_000
        })
        resp = client.get("/api/budgets?month=5&year=2026")
        assert resp.status_code == 200
        budgets = resp.get_json()["data"]
        assert len(budgets) == 1
        b = budgets[0]
        assert "nama_kategori" in b
        assert b["nama_kategori"] == "Makan"
        assert "persen_terpakai" in b


# ============================================================
# VIEW PROTECTION (redirect ke /login jika belum login)
# ============================================================
class TestViewProtection:
    def test_dashboard_redirect_ke_login(self, client):
        """GET /dashboard tanpa login harus redirect ke /login."""
        # Logout dulu untuk memastikan tidak ada sesi aktif
        client.post("/api/auth/logout")
        resp = client.get("/dashboard")
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_transactions_redirect_ke_login(self, client):
        """GET /transactions tanpa login harus redirect ke /login."""
        client.post("/api/auth/logout")
        resp = client.get("/transactions")
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_wallets_redirect_ke_login(self, client):
        """GET /wallets tanpa login harus redirect ke /login."""
        client.post("/api/auth/logout")
        resp = client.get("/wallets")
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_goals_redirect_ke_login(self, client):
        """GET /goals tanpa login harus redirect ke /login."""
        client.post("/api/auth/logout")
        resp = client.get("/goals")
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_dashboard_accessible_setelah_login(self, client):
        """GET /dashboard setelah login harus return 200."""
        _auth(client, "dashlogin@test.com")
        resp = client.get("/dashboard")
        assert resp.status_code == 200

    def test_settings_accessible_setelah_login(self, client):
        """GET /settings setelah login harus return 200."""
        _auth(client, "setlogin@test.com")
        resp = client.get("/settings")
        assert resp.status_code == 200
