"""Test landing page publik di root URL `/`.

Perilaku yang diuji:
- Tamu (anonim) yang membuka `/` melihat landing page (200), bukan redirect.
- Landing page memuat penanda produk + tombol CTA Daftar/Masuk.
- Landing page menautkan ke halaman /login dan /register.
- Pengguna yang sudah login tetap diarahkan (302) ke /dashboard.
"""


def register(client, email="landing@test.com", password="pass123", name="User Landing"):
    """Bantu daftar via API (membuat sesi belum login)."""
    return client.post("/api/auth/register",
                       json={"email": email, "password": password, "name": name})


def login(client, email="landing@test.com", password="pass123"):
    """Bantu login via API agar test client punya sesi terautentikasi."""
    return client.post("/api/auth/login", json={"email": email, "password": password})


class TestLandingAnonim:
    def test_root_anonim_menampilkan_landing(self, client):
        """`GET /` tanpa login → 200 dan memuat penanda landing (bukan redirect)."""
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        # Penanda produk dan ajakan utama
        assert "ReTrack" in body
        assert "Daftar" in body
        assert "Masuk" in body

    def test_landing_menautkan_login_dan_register(self, client):
        """Landing memuat tautan ke /login dan /register untuk CTA."""
        resp = client.get("/")
        body = resp.data.decode("utf-8")
        assert "/login" in body
        assert "/register" in body


class TestLandingTerautentikasi:
    def test_root_setelah_login_redirect_dashboard(self, client):
        """`GET /` saat sudah login → 302 menuju /dashboard."""
        register(client)
        login(client)
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/dashboard" in resp.headers["Location"]
