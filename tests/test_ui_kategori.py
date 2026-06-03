"""Test UI: quick-add kategori (Transaksi) & pemilih ikon popup (Kategori).

Bagian 5 (sesi 2026-06-03). Murni frontend; endpoint & skema kategori TIDAK
berubah. Yang diuji:
1. Template transaksi memuat komponen quick-add (tombol "+" + panel Alpine).
2. Template kategori memuat struktur pemilih ikon (hidden #kat-ikon + tombol
   pemicu + popup grid + kotak cari), bukan lagi input teks bebas.
3. Penegasan API: POST/PUT /api/categories menerima `icon` & membalas `id`.
"""


def _auth(client, email="ui@test.com", password="pass123", name="User UI"):
    """Helper: register + login via API."""
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


class TestQuickAddTransaksi:
    def test_transaksi_memuat_quick_add(self, client):
        """Halaman transaksi memuat tombol "+" + komponen Alpine quick-add."""
        _auth(client, "uiqa@test.com")
        resp = client.get("/transactions")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert "quickAddKategori()" in body   # factory Alpine
        assert "quick-add-btn" in body         # tombol "+"
        assert "quick-add-panel" in body       # panel inline (1 input nama)


class TestIconPickerKategori:
    def test_kategori_memuat_hidden_input_ikon(self, client):
        """Input ikon kini hidden — id/name dipertahankan agar simpanKategori jalan."""
        _auth(client, "uihidden@test.com")
        resp = client.get("/categories")
        assert resp.status_code == 200
        body = resp.data.decode("utf-8")
        assert 'type="hidden" id="kat-ikon"' in body
        assert 'name="icon"' in body

    def test_kategori_memuat_pemicu_dan_popup(self, client):
        """Halaman kategori memuat tombol pemicu + popup grid ikon + kotak cari."""
        _auth(client, "uipopup@test.com")
        resp = client.get("/categories")
        body = resp.data.decode("utf-8")
        assert "icon-picker-trigger" in body
        assert 'id="modal-pilih-ikon"' in body
        assert 'id="grid-ikon"' in body
        assert "IKON_KURASI" in body            # daftar ikon kurasi
        assert 'id="cari-ikon"' in body          # kotak cari
        assert 'id="ikon-manual"' in body        # fallback ketik manual

    def test_input_teks_ikon_lama_diganti(self, client):
        """#kat-ikon tidak lagi berupa input teks bebas."""
        _auth(client, "uiold@test.com")
        resp = client.get("/categories")
        body = resp.data.decode("utf-8")
        assert 'type="text" id="kat-ikon"' not in body


class TestCategoryIconAPI:
    def test_post_kategori_dengan_ikon(self, client):
        """POST /api/categories menerima `icon` dan membalas id + icon."""
        _auth(client, "apiicon@test.com")
        resp = client.post("/api/categories", json={
            "name": "Makan", "kind": "expense", "icon": "restaurant"
        })
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert "id" in data
        assert data["icon"] == "restaurant"
        assert data["kind"] == "expense"

    def test_put_kategori_ganti_ikon(self, client):
        """PUT /api/categories/<id> dapat mengubah `icon`."""
        _auth(client, "apiiconput@test.com")
        cid = client.post("/api/categories", json={
            "name": "Transport", "kind": "expense", "icon": "directions_bus"
        }).get_json()["data"]["id"]
        resp = client.put(f"/api/categories/{cid}", json={"icon": "train"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["icon"] == "train"

    def test_post_kategori_tanpa_ikon_tetap_valid(self, client):
        """POST tanpa `icon` tetap valid (kolom icon nullable)."""
        _auth(client, "apinoicon@test.com")
        resp = client.post("/api/categories", json={"name": "Gaji", "kind": "income"})
        assert resp.status_code == 201
        assert resp.get_json()["data"]["icon"] is None
