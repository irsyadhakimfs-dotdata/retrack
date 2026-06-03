# Rencana Implementasi — Navigasi Mobile ver2

> **Untuk pekerja agentik:** SUB-SKILL WAJIB: gunakan superpowers:subagent-driven-development (disarankan) atau superpowers:executing-plans untuk mengerjakan rencana ini tugas-demi-tugas. Langkah memakai sintaks checkbox (`- [ ]`) untuk pelacakan.

**Goal:** Hapus bilah navigasi bawah (bottom-nav) di mobile, perbaiki tombol hamburger agar membuka sidebar drawer, dan tambahkan FAB "Tambah Transaksi" sebagai pintasan mobile.

**Arsitektur:** Mekanisme drawer (`.sidebar.open`, `.sidebar-overlay`, `toggleSidebar()`/`closeSidebar()`) sudah ada penuh — kita hanya membebaskannya dari bug double-fire. Bottom-nav dinonaktifkan dengan mengomentari include-nya (file partial & CSS dibiarkan agar mudah dikembalikan). FAB adalah `<a>` melayang yang dirender di `base.html` untuk semua halaman terproteksi **kecuali** Transaksi, menaut ke `/transactions?new=1`; halaman Transaksi membaca `?new=1` saat load lalu membuka modal tambah otomatis.

**Tech Stack:** Flask + Jinja2, Tailwind (CDN), CSS kustom (`custom.css` + legacy `style.css`), vanilla JS (`main.js` + inline), Pytest (test client merender HTML).

---

## Temuan Kunci (konteks sebelum mulai)

- **Bug hamburger = double-fire.** `base.html:84` punya `onclick="toggleSidebar()"` **dan** `main.js:180` memasang `addEventListener('click', toggleSidebar)`. Tiap tap menjalankan toggle dua kali → buka lalu langsung tutup → terlihat tidak berfungsi. Dev sudah mendokumentasikan pola yang benar untuk theme-toggle ("event listener HANYA di main.js … agar tidak double-fire"); hamburger tinggal mengikuti pola itu.
- **Drawer sudah lengkap.** `style.css:1447-1453` membuat `.sidebar` slide-in di ≤768px; `style.css:1467` menampilkan `.hamburger-btn`; `style.css:1116-1126` mengatur `.sidebar-overlay`. Tidak perlu CSS drawer baru.
- **Disable include WAJIB pakai komentar Jinja `{# #}`.** Komentar HTML `<!-- {% include %} -->` TETAP mengeksekusi `{% include %}` karena Jinja memproses tag di dalam komentar HTML. Hanya `{# … #}` yang benar-benar menonaktifkan.
- **Form tambah transaksi = modal lokal.** `#modal-tambah-transaksi` hanya ada di `transactions/index.html`, dibuka oleh `bukaModalTambah()` (baris 520). Init halaman `inisialisasiHalaman()` (baris 221, async) memuat kategori+wallet lebih dulu — auto-open harus menunggu init selesai agar dropdown terisi.
- **Pola test rendering.** `tests/test_navigation.py` + `tests/conftest.py`: helper register+login lalu `client.get("/halaman")` dan assert string pada HTML terender. Kita pakai pola sama.

---

## Struktur File

| File | Tindakan | Tanggung jawab |
|------|----------|----------------|
| `app/templates/base.html` | Modifikasi | Hapus inline onclick hamburger; komentari include bottom-nav; render FAB |
| `app/static/css/custom.css` | Modifikasi | Tambah section `.fab` (mobile-only) |
| `app/templates/transactions/index.html` | Modifikasi | Auto-open modal tambah saat `?new=1` |
| `tests/test_mobile_nav_ver2.py` | Buat | Regресi: bottom-nav hilang, hamburger tanpa onclick, FAB muncul/sembunyi, auto-open ada |
| `app/templates/partials/_bottomnav.html` | **Tidak disentuh** | Dibiarkan (pilihan "nonaktifkan saja") |

Catatan: blok CSS `.bottom-nav` (custom.css:716-784) sengaja **dibiarkan**. Aturan `.main-content { padding-bottom }` di dalamnya tetap berlaku → menjadi ruang aman agar FAB tidak menutupi konten.

---

## Task 1: Nonaktifkan bottom navigation bar

**Files:**
- Modify: `app/templates/base.html:148-150`
- Test: `tests/test_mobile_nav_ver2.py` (buat baru)

- [ ] **Step 1: Tulis test yang gagal**

Buat `tests/test_mobile_nav_ver2.py`:

```python
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
```

- [ ] **Step 2: Jalankan test untuk memastikan GAGAL**

Run: `pytest tests/test_mobile_nav_ver2.py::test_bottom_nav_dinonaktifkan -v`
Expected: FAIL — `assert 'class="bottom-nav"' not in body` (bottom-nav masih dirender).

- [ ] **Step 3: Implementasi — komentari include dengan sintaks Jinja**

Di `app/templates/base.html`, ganti baris 148-150:

```html
  <!-- ===== Bottom Navigation (mobile, ≤768px) ===== -->
  {% include 'partials/_bottomnav.html' %}
  <!-- /bottom-nav -->
```

menjadi:

```html
  {# ===== Bottom Navigation (mobile) — DINONAKTIFKAN ver2 =====
     Navigasi mobile kini lewat hamburger → sidebar drawer + FAB tambah-transaksi.
     Partial _bottomnav.html & CSS .bottom-nav sengaja dibiarkan agar mudah dikembalikan.
  {% include 'partials/_bottomnav.html' %}
  #}
```

- [ ] **Step 4: Jalankan test untuk memastikan LULUS**

Run: `pytest tests/test_mobile_nav_ver2.py::test_bottom_nav_dinonaktifkan -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/base.html tests/test_mobile_nav_ver2.py
git commit -m "feat(mobile): nonaktifkan bottom navigation bar (ver2)"
```

---

## Task 2: Perbaiki tombol hamburger (hapus double-fire)

**Files:**
- Modify: `app/templates/base.html:84`
- Test: `tests/test_mobile_nav_ver2.py` (tambah fungsi)

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan ke `tests/test_mobile_nav_ver2.py`:

```python
def test_hamburger_tanpa_inline_onclick(client):
    """Hamburger tetap ada, tapi tanpa onclick toggleSidebar() (cegah double-fire)."""
    _auth(client, "ver2ham@test.com")
    body = client.get("/dashboard").data.decode("utf-8")
    assert "hamburger-btn" in body
    assert "toggleSidebar()" not in body
```

Catatan: assertion `"toggleSidebar()" not in body` baru valid setelah Task 1 (tombol "Lainnya" di bottom-nav juga memakai onclick itu). Karena Task 1 sudah selesai, satu-satunya sisa `toggleSidebar()` adalah inline onclick hamburger.

- [ ] **Step 2: Jalankan test untuk memastikan GAGAL**

Run: `pytest tests/test_mobile_nav_ver2.py::test_hamburger_tanpa_inline_onclick -v`
Expected: FAIL — `assert "toggleSidebar()" not in body` (masih ada inline onclick di hamburger).

- [ ] **Step 3: Implementasi — hapus inline onclick**

Di `app/templates/base.html`, ganti baris 84:

```html
      <button class="hamburger-btn" onclick="toggleSidebar()" aria-label="Buka menu">
```

menjadi:

```html
      <button class="hamburger-btn" aria-label="Buka menu">
```

Listener tetap dipasang di `main.js:180` (`addEventListener('click', toggleSidebar)`) — tidak ada perubahan JS yang diperlukan.

- [ ] **Step 4: Jalankan test untuk memastikan LULUS**

Run: `pytest tests/test_mobile_nav_ver2.py::test_hamburger_tanpa_inline_onclick -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/base.html tests/test_mobile_nav_ver2.py
git commit -m "fix(mobile): hamburger double-fire — hapus inline onclick (ver2)"
```

---

## Task 3: Render FAB "Tambah Transaksi" di base.html

**Files:**
- Modify: `app/templates/base.html` (tambah markup FAB sebelum blok bottom-nav, ~baris 147, di dalam `.app-layout`)
- Test: `tests/test_mobile_nav_ver2.py` (tambah 2 fungsi)

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan ke `tests/test_mobile_nav_ver2.py`:

```python
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
```

- [ ] **Step 2: Jalankan test untuk memastikan GAGAL**

Run: `pytest tests/test_mobile_nav_ver2.py::test_fab_muncul_di_halaman_non_transaksi tests/test_mobile_nav_ver2.py::test_fab_tidak_muncul_di_halaman_transaksi -v`
Expected: FAIL — `assert 'class="fab"' in body` (FAB belum ada).

- [ ] **Step 3: Implementasi — tambah markup FAB**

Di `app/templates/base.html`, tepat **sebelum** blok komentar Bottom Navigation (sekitar baris 147, masih di dalam `<div class="app-layout">`), sisipkan:

```html
  {# ===== FAB Tambah Transaksi (mobile saja; disembunyikan di halaman Transaksi) =====
     Pintasan ke halaman Transaksi dengan ?new=1 → modal tambah terbuka otomatis. #}
  {% if current_user.is_authenticated and request.blueprint != 'transaction_views' %}
  <a class="fab" href="{{ url_for('transaction_views.transactions') }}?new=1"
     aria-label="Tambah transaksi">
    <span class="material-symbols-outlined">add</span>
  </a>
  {% endif %}
```

- [ ] **Step 4: Jalankan test untuk memastikan LULUS**

Run: `pytest tests/test_mobile_nav_ver2.py -k fab -v`
Expected: PASS (kedua test fab).

- [ ] **Step 5: Commit**

```bash
git add app/templates/base.html tests/test_mobile_nav_ver2.py
git commit -m "feat(mobile): render FAB tambah-transaksi di base (ver2)"
```

---

## Task 4: Styling FAB (.fab) di custom.css

**Files:**
- Modify: `app/static/css/custom.css` (tambah section baru di akhir file)

Tidak ada test pytest untuk CSS — verifikasi visual via headless Chrome (Task 6). `var(--grad-brand)` dipakai di custom.css:777 dan `var(--safe-bottom)` didefinisikan di custom.css:706, jadi keduanya pasti tersedia.

- [ ] **Step 1: Tambahkan section `.fab` di akhir `app/static/css/custom.css`**

```css
/* ---------------------------------------------------------
   20. FAB "Tambah Transaksi" (mobile) — ver2
   Tombol melayang kanan-bawah, pintasan ke halaman Transaksi.
   Hanya tampil ≤768px (desktop sidebar selalu kelihatan).
   z-index 90 → di bawah overlay drawer/modal (≥99) sehingga
   tertutup rapi saat drawer atau bottom-sheet terbuka.
   --------------------------------------------------------- */
.fab { display: none; }

@media (max-width: 768px) {
  .fab {
    position: fixed;
    right: 1.1rem;
    bottom: calc(1.1rem + var(--safe-bottom));
    z-index: 90;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 9999px;
    background: var(--grad-brand);
    color: #fff;
    box-shadow: 0 10px 28px -8px rgba(99, 102, 241, 0.6);
    text-decoration: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .fab:hover { color: #fff; text-decoration: none; }
  .fab:active { transform: scale(0.93); }
  .fab .material-symbols-outlined {
    font-size: 1.75rem;
    font-variation-settings: 'wght' 500;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fab { transition: none; }
}
```

- [ ] **Step 2: Verifikasi cepat tidak ada regresi backend**

Run: `pytest tests/test_mobile_nav_ver2.py -v`
Expected: PASS (CSS tidak memengaruhi assertion HTML; sekadar memastikan tidak ada yang rusak).

- [ ] **Step 3: Commit**

```bash
git add app/static/css/custom.css
git commit -m "feat(mobile): styling FAB tambah-transaksi (ver2)"
```

---

## Task 5: Auto-open modal tambah saat datang dari FAB (?new=1)

**Files:**
- Modify: `app/templates/transactions/index.html:683-684` (handler DOMContentLoaded)
- Test: `tests/test_mobile_nav_ver2.py` (tambah fungsi)

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan ke `tests/test_mobile_nav_ver2.py`:

```python
def test_transaksi_punya_auto_open_dari_fab(client):
    """Halaman Transaksi memuat logika auto-open modal saat datang dari FAB (?new=1)."""
    _auth(client, "ver2auto@test.com")
    body = client.get("/transactions").data.decode("utf-8")
    assert "auto-open" in body
```

(Penanda `auto-open` berasal dari komentar pada kode yang ditambahkan di Step 3, sehingga test stabil terhadap perubahan detail.)

- [ ] **Step 2: Jalankan test untuk memastikan GAGAL**

Run: `pytest tests/test_mobile_nav_ver2.py::test_transaksi_punya_auto_open_dari_fab -v`
Expected: FAIL — `assert "auto-open" in body`.

- [ ] **Step 3: Implementasi — tunggu init lalu buka modal bila ?new=1**

Di `app/templates/transactions/index.html`, ganti baris 683-684:

```js
document.addEventListener('DOMContentLoaded', function () {
  inisialisasiHalaman();
```

menjadi:

```js
document.addEventListener('DOMContentLoaded', function () {
  // auto-open: bila datang dari FAB (?new=1), buka modal tambah setelah init selesai
  inisialisasiHalaman().then(function () {
    if (new URLSearchParams(window.location.search).get('new') === '1') {
      bukaModalTambah();
      // Bersihkan param agar refresh tidak membuka modal lagi
      history.replaceState({}, '', window.location.pathname);
    }
  });
```

Penting: `inisialisasiHalaman()` async dan memuat kategori dulu; `.then()` memastikan dropdown sudah terisi sebelum `bukaModalTambah()` dipanggil. Sisa handler (search debounce, listener radio tipe) tidak berubah — biarkan baris setelahnya apa adanya.

- [ ] **Step 4: Jalankan test untuk memastikan LULUS**

Run: `pytest tests/test_mobile_nav_ver2.py::test_transaksi_punya_auto_open_dari_fab -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templates/transactions/index.html tests/test_mobile_nav_ver2.py
git commit -m "feat(mobile): auto-open modal tambah dari FAB ?new=1 (ver2)"
```

---

## Task 6: Verifikasi akhir (regresi + QA visual)

**Files:** tidak ada perubahan kode — hanya verifikasi.

- [ ] **Step 1: Jalankan seluruh suite test (regresi)**

Run: `pytest`
Expected: semua PASS (termasuk 5 test baru di `test_mobile_nav_ver2.py`; `test_navigation.py` tetap hijau).

- [ ] **Step 2: Jalankan app & QA visual di viewport mobile**

Jalankan `flask run`, lalu pakai teknik headless Chrome (lihat memori "Visual QA via headless Chrome" — perhatikan gotcha pin viewport ~472px) untuk memeriksa pada lebar mobile:

1. **Hamburger** — tap ikon ☰ di topbar → drawer sidebar meluncur masuk; tap overlay / tekan Escape → menutup. (Sebelumnya tidak bereaksi.)
2. **Bottom bar** — tidak ada lagi bilah navigasi di bawah pada semua halaman.
3. **FAB** — tombol bulat "+" tampak kanan-bawah di Dashboard/Anggaran/dll; **tidak** tampak di halaman Transaksi.
4. **Alur FAB** — dari Dashboard, tap FAB → pindah ke halaman Transaksi dan modal "Tambah Transaksi" terbuka otomatis dengan dropdown kategori terisi; URL bersih tanpa `?new=1` setelahnya.
5. **Desktop** — pada lebar ≥769px: sidebar tetap menetap, hamburger & FAB tersembunyi (tidak ada regresi).

- [ ] **Step 3: Catat hasil & commit dokumentasi (opsional, ikut konvensi proyek)**

Bila perlu, perbarui `MOBILE_LOG_UPDATE.md` / `next_step.md` sesuai konvensi proyek, lalu:

```bash
git add MOBILE_LOG_UPDATE.md next_step.md
git commit -m "docs(mobile): catat hasil ver2 (bottom-nav off, hamburger, FAB)"
```

---

## Self-Review (cek terhadap rancangan)

- **Cakupan spec:** (1) hapus bottom-nav → Task 1; (2) hamburger buka sidebar → Task 2 (mekanisme drawer sudah ada); (3) FAB tambah-transaksi → Task 3+4 (markup+CSS); perilaku FAB ke halaman Transaksi + auto-open → Task 5; FAB sembunyi di halaman Transaksi → Task 3. Semua tercakup.
- **Konsistensi nama:** `bukaModalTambah()`, `inisialisasiHalaman()`, `toggleSidebar()`, kelas `.fab`, `.hamburger-btn`, `.bottom-nav` — sesuai sumber.
- **Tanpa placeholder:** semua langkah berisi kode/perintah konkret.
- **Urutan penting:** Task 1 (disable bottom-nav) mendahului Task 2 (hamburger) agar assertion `"toggleSidebar()" not in body` valid. Task 5 bergantung pada FAB (Task 3) yang mengirim `?new=1`.
- **Pilihan "nonaktifkan saja":** dihormati — `_bottomnav.html` & blok CSS `.bottom-nav` tidak dihapus.
