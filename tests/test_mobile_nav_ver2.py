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


def test_hamburger_tanpa_inline_onclick(client):
    """Hamburger tetap ada, tapi tanpa onclick toggleSidebar() (cegah double-fire)."""
    _auth(client, "ver2ham@test.com")
    body = client.get("/dashboard").data.decode("utf-8")
    assert "hamburger-btn" in body
    assert "toggleSidebar()" not in body


def test_fab_muncul_di_halaman_non_transaksi(client):
    """FAB tambah-transaksi muncul di dashboard, menaut ke transaksi dengan ?new=1."""
    _auth(client, "ver2fab@test.com")
    body = client.get("/dashboard").data.decode("utf-8")
    assert 'class="fab"' in body
    assert "?new=1" in body


def test_fab_tidak_muncul_di_halaman_transaksi(client):
    """FAB disembunyikan di halaman Transaksi (sudah ada tombol Tambah di header)."""
    _auth(client, "ver2fabtx@test.com")
    body = client.get("/transactions").data.decode("utf-8")
    assert 'class="fab"' not in body
