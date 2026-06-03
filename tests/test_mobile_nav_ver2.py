"""Test ver2: nonaktifkan bottom-nav, perbaiki hamburger, tambah FAB tambah-transaksi.

Lihat ver2.md. Menguji HTML terender pada halaman terproteksi memakai test client.
"""


def _auth(client, email, password="pass123", name="User Ver2"):
    """Helper: register + login via API agar client punya sesi terautentikasi."""
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


def test_bottom_nav_dinonaktifkan(client):
    """Bilah navigasi bawah tidak lagi dirender di halaman terproteksi."""
    _auth(client, "ver2bn@test.com")
    body = client.get("/dashboard").data.decode("utf-8")
    assert 'class="bottom-nav"' not in body
