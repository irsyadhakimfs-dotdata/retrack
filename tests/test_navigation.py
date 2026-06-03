"""Test navigasi global: menu profil (akun + logout) di topbar.

Bagian 6 (sesi 2026-06-03): di mobile sebelumnya tidak ada jalan ke logout
maupun halaman akun. Kini `base.html` menampilkan menu profil di topbar pada
SEMUA halaman terproteksi. Uji bahwa halaman terproteksi memuat penanda menu
beserta tautan ke /logout dan /settings, serta inisial nama pada avatar.
"""


def _auth(client, email="nav@test.com", password="pass123", name="User Nav"):
    """Helper: register + login via API agar client punya sesi terautentikasi."""
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


class TestMenuProfilTopbar:
    def test_dashboard_memuat_menu_profil(self, client):
        """Halaman terproteksi memuat menu profil + tautan logout & akun."""
        _auth(client, "navdash@test.com", name="Budi")
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "profile-menu" in body
        assert "profile-avatar" in body
        assert "/logout" in body
        assert "/settings" in body

    def test_inisial_avatar_dari_nama(self, client):
        """Avatar menampilkan inisial (huruf pertama nama, dikapitalkan server-side)."""
        _auth(client, "navinit@test.com", name="budi")
        resp = client.get("/dashboard")
        body = resp.data.decode("utf-8")
        # 'budi' → inisial 'B' di dalam <span class="profile-avatar">B</span>
        assert 'class="profile-avatar">B<' in body

    def test_menu_profil_di_halaman_transaksi(self, client):
        """Menu profil juga muncul di halaman lain (mis. transaksi)."""
        _auth(client, "navtrx@test.com")
        resp = client.get("/transactions")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "profile-menu" in body
        assert "/logout" in body
