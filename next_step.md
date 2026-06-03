# next_step.md — Panduan Sesi Berikutnya: Membuat Landing Page

> **Dokumen ini adalah jembatan antar-sesi.** Ditulis di akhir sesi *deployment
> readiness audit + setup Vercel*, untuk membimbing sesi berikutnya yang tugas
> utamanya adalah **membuat landing page** ReTrack.
>
> Baca **Bagian 1–2** dulu (konteks), lalu kerjakan **Bagian 3** (tugas).
> Jangan lewati **Bagian 2.3** dan **Bagian 4** — di situ ada jebakan penting.

---

## 0. Cara pakai dokumen ini

1. Baca `CLAUDE.md` (sumber kebenaran proyek) **tetapi** lihat peringatan di
   **Bagian 2.3** — sebagian isi CLAUDE.md soal warna/font sudah **kedaluwarsa**;
   kode adalah kebenaran sebenarnya.
2. Pahami status deployment (Bagian 1) supaya tidak mengulang setup.
3. Kerjakan landing page mengikuti spesifikasi Bagian 3.
4. Pakai TodoWrite untuk melacak sub-tugas Bagian 3.

---

## 1. STATUS PROYEK SAAT INI (ringkasan sesi sebelumnya)

### 1.1 Deployment sudah HIDUP (Vercel + Neon)

| Item | Nilai |
|---|---|
| GitHub repo | `github.com/irsyadhakimfs-dotdata/retrack`, branch **`main`** |
| Commit terakhir | `98f11b4` ("chore: siapkan deployment Vercel …") |
| Vercel project | `irsyad-hakims-projects/retrack` (`prj_0z2xk4AfgO5PCDypO6t4MqRkacUr`) |
| Link lokal | `.vercel/repo.json` (gitignored) |
| Database | **Neon** `neon-violet-field`, ter-connect ke project |
| Skema DB | **12 tabel** sudah dibuat otomatis di Neon (7 OLTP + 5 `dwh_*`) |
| Preview URL | `https://retrack-l1bv4jsfi-irsyad-hakims-projects.vercel.app` (status READY) |
| Verifikasi | `/ping` → `{"ok": true, "message": "pong"}` ✓ ; koneksi Neon ✓ |
| Runtime Vercel | Python 3.12, `@vercel/python`, dependency via `uv` |

> **Production belum dipromosikan.** Deploy terakhir baru **preview**
> (`vercel deploy`). Promosi ke production (`vercel --prod`) **menunggu
> konfirmasi user** dan belum dijalankan. Lihat **Bagian 3.8**.

### 1.2 Refactor kode yang sudah dilakukan agar kompatibel Vercel

Jangan diubah balik — ini fondasi deploy:

- **`api/index.py`** *(baru)* — entrypoint WSGI Vercel. Membuat `app` via
  `create_app("production")` dan menjalankan `db.create_all()` saat cold start
  (di-gate env `AUTO_CREATE_DB=1`, dibungkus try/except agar app tetap start).
- **`vercel.json`** *(baru)* — build `@vercel/python` dari `api/index.py`;
  semua route (termasuk `/static/*`) diarahkan ke fungsi serverless itu.
  → **Artinya CSS/JS/gambar di `app/static/` tetap dilayani oleh Flask di
  Vercel.** Tidak perlu perlakuan khusus untuk aset landing page.
- **`app/config.py`** — `ProdConfig` kini memakai `_normalize_db_url()` yang
  mengubah `postgres://` → `postgresql://` (Neon kadang pakai prefix lama) dan
  fallback aman ke SQLite bila `DATABASE_URL` kosong.
- **`app/services/market_service.py`** — `import yfinance` dibuat **opsional**
  (`try/except → yf=None`). Di Vercel yfinance tidak dipasang (terlalu besar);
  fitur market otomatis jatuh ke fallback HTTP gratis. **Fitur tetap utuh.**
- **`requirements.txt`** — ramping untuk produksi (tambah `psycopg2-binary`,
  tanpa `yfinance`/`pytest`). **`requirements-dev.txt`** *(baru)* = full stack
  lokal (`-r requirements.txt` + `yfinance` + `pytest`).
- **`.gitignore`** — tambah `instance/`, `.vercel/`, `node_modules/`, `*.sqlite`.
  Vercel juga otomatis menambah `.env.local`.

### 1.3 Environment variables di Vercel

Sudah di-set (terenkripsi):

| Key | Production | Development | Preview | Catatan |
|---|:--:|:--:|:--:|---|
| `SECRET_KEY` | ✅ | ✅ | ⚠️ | nilai acak kuat |
| `FLASK_ENV` = `production` | ✅ | ✅ | ⚠️ | |
| `AUTO_CREATE_DB` = `1` | ✅ | ✅ | ⚠️ | |
| `DATABASE_URL` (+ `POSTGRES_*`, `PG*`) | ✅ | ✅ | ✅ | di-inject oleh integrasi Neon |

> ⚠️ **TODO terbawa:** menambah `SECRET_KEY`/`FLASK_ENV`/`AUTO_CREATE_DB` ke
> environment **Preview** sempat **gagal** karena bug CLI Vercel v54.7.1
> (crash saat target `preview`). Tidak memblokir production. Kalau perlu deploy
> preview yang aman, set lewat **dashboard Vercel** (Settings → Environment
> Variables) atau coba `vercel env add <NAME> preview --value <v> --yes`.

### 1.4 Catatan lingkungan lokal

- `.env.local` **ada di lokal** (di-pull `vercel`, berisi kredensial Neon asli) —
  **gitignored, JANGAN commit**.
- `psycopg2-binary` sudah ter-install di Python lokal (Python 3.12).
- **124 test lulus** (`pytest`). Pertahankan hijau.
- `vercel` CLI ter-install global. Login sebagai `irsyadhakimfs-dotdata`.

---

## 2. PENGETAHUAN KONTEKSTUAL (wajib sebelum menyentuh frontend)

### 2.1 Arsitektur & lapisan (dari CLAUDE.md — masih berlaku)

Application factory `create_app()` di `app/__init__.py`. Pisahkan TEGAS:
`models/` (tabel) · `api/` (REST JSON) · `services/` (logika bisnis) ·
`views/` (render HTML). Landing page = **view** → file view di `app/views/`,
template di `app/templates/`.

### 2.2 Routing & autentikasi (relevan untuk landing)

- Root `/` ditangani **`app/views/auth_views.py` → `index()`**.
  Saat ini: authenticated → `/dashboard`, anonim → **redirect `/login`**.
- Endpoint untuk tombol CTA:
  - `url_for('auth_views.login')` → `/login`
  - `url_for('auth_views.register')` → `/register`
  - `url_for('dashboard_views.dashboard')` → `/dashboard` (login_required)
- **Tidak ada test** yang mengecek perilaku `GET /` anonim → aman diubah jadi
  render landing page (test proteksi view hanya menyasar `/dashboard`,
  `/transactions`, dll, jadi tidak terpengaruh).

### 2.3 ⚠️ SISTEM DESAIN SEBENARNYA (CLAUDE.md kedaluwarsa di poin ini!)

`CLAUDE.md` menulis brand **teal/pink + font Manrope**. **Itu sudah usang.**
Implementasi nyata di `base.html` & `static/css/custom.css` adalah:

**Brand: Indigo + Amber (fintech modern).** Ikuti yang INI agar landing page
seragam dengan aplikasi:

| Token | Nilai | Peran |
|---|---|---|
| `--primary` / `colors.primary` | `#6366F1` (indigo-500) | brand utama, tombol, link, fokus |
| `--primary-dark` | `#4F46E5` / `#4338CA` | hover/gradien |
| `--primary-light` | `#EEF0FE` | latar lembut |
| `--accent` / `colors.accent` | `#F59E0B` (amber-500) | aksen/pop (pakai teks gelap di atasnya) |
| `--pos` | `#10B981` (emerald) | pemasukan/positif |
| `--neg` | `#F43F5E` (rose) | pengeluaran/negatif |
| Font isi (`font-sans`) | **Plus Jakarta Sans** | body |
| Font display (`font-display`) | **Space Grotesk** | judul & angka besar |

**Gradien siap pakai (CSS variables di `custom.css`)** — gunakan ulang, jangan
bikin warna acak:
- `--grad-brand` indigo→indigo-dark · `--grad-hero` indigo→violet→amber
  (cocok untuk hero landing) · `--grad-accent` amber · `--grad-saldo`,
  `--grad-income`, `--grad-expense`, `--grad-net`.

**Glass tokens:** `--glass-bg: rgba(255,255,255,0.72)`, `--glass-border`,
`--glass-blur: 18px`. Strategi "permukaan campur": nav/topbar/hero = glass,
kartu konten = solid (kontras teks lebih baik).

**Dark mode:** via atribut `data-theme="dark"` di `<html>`. Disimpan di
`localStorage('refinance-theme')`, di-toggle oleh `main.js`. Tailwind dikonfig
`darkMode: ['selector','[data-theme="dark"]']` → boleh pakai varian `dark:`.
**Wajib** sertakan skrip inline anti-FOUC di `<head>` (lihat pola di Bagian 3.5).

**Tailwind:** Play CDN, `preflight: false` (reset dimatikan agar `style.css`
legacy tidak rusak). Konfigurasi penuh ada di `base.html` baris 19–44 — **salin
blok `tailwind.config` yang sama** ke landing page (karena landing standalone).

> **Saran (opsional):** perbarui bagian "Aspek Desain" di `CLAUDE.md` agar
> menyebut Indigo/Amber + Plus Jakarta Sans/Space Grotesk, supaya tidak
> menyesatkan sesi mendatang. Konfirmasi ke user dulu sebelum mengubah CLAUDE.md.

### 2.4 Aturan frontend (WAJIB, dari CLAUDE.md — masih berlaku)

1. **Tailwind utility-first.** Custom CSS **hanya** di `static/css/custom.css`.
2. **Alpine.js** untuk reaktivitas (mis. toggle menu mobile, dropdown).
   **JANGAN jQuery.**
3. **Chart.js** untuk semua chart (kemungkinan tak perlu di landing).
4. **Material Symbols Outlined** untuk ikon. **JANGAN emoji** (kesan AI).
5. **UI Bahasa Indonesia.** Komentar kode Python pakai `#` Bahasa Indonesia.
6. **Setiap halaman `extends base.html` KECUALI landing** → landing page
   **berdiri sendiri** (HTML penuh sendiri), seperti pola `auth/login.html`.

### 2.5 Aset & logo

Pakai aset di **`app/static/img/`** (dilayani Flask, juga di Vercel):
- `logo-light.png` — logo untuk mode terang
- `logo-dark.png` — logo untuk mode gelap (swap via kelas `.logo-light`/`.logo-dark` + `.app-logo-img` di `custom.css`)
- `logo-32.png` — favicon

> Jangan pakai `assets/Logo_ReTrack.png` di root repo — folder itu **tidak**
> dilayani Flask.

---

## 3. TUGAS LANDING PAGE — ✅ SELESAI (sesi 2026-06-02)

> Landing page sudah dibuat & ter-commit (`app/templates/landing.html`,
> `auth_views.index()`, `tests/test_landing.py`). Bagian 3 di bawah disimpan
> sebagai arsip konteks. **TUGAS AKTIF BERIKUTNYA ADA DI BAGIAN 5.**

### 3.1 Tujuan & ruang lingkup

Buat **halaman landing publik** untuk pengunjung yang **belum login** di URL
`/`. Tujuannya memperkenalkan ReTrack (financial & budget planner untuk anak
muda Indonesia 18–30 th) dan mendorong **Daftar / Masuk**. Tanpa mengubah fitur
dashboard atau backend yang sudah ada.

### 3.2 Keputusan yang perlu dikonfirmasi ke user sebelum/di awal coding

1. **Ganti perilaku `/`?** Rekomendasi: anonim `/` → render `landing.html`
   (bukan lagi redirect ke `/login`). User yang sudah login tetap → dashboard.
2. **Konten/section** mana yang diinginkan (lihat default di 3.4).
3. **Nada & copy**: serius-fintech vs ramah-mahasiswa. Default: ramah &
   ringkas, Bahasa Indonesia.
4. Perlu **toggle dark mode** di landing? Default: ya (konsisten dgn app).

(Gunakan AskUserQuestion bila perlu, tapi jangan blocking untuk hal sepele —
pakai default lalu sebutkan asumsinya.)

### 3.3 File yang dibuat / diubah

| File | Aksi |
|---|---|
| `app/templates/landing.html` | **BARU** — halaman standalone (tidak extends base.html) |
| `app/views/auth_views.py` | **UBAH** `index()`: anonim → `render_template('landing.html')` |
| `app/static/css/custom.css` | (opsional) tambah kelas `.landing-*` bila utility Tailwind tak cukup |
| `tests/test_landing.py` | **BARU** — test rute landing |
| `CLAUDE.md` | (opsional, konfirmasi dulu) sinkronkan deskripsi brand |

Contoh perubahan `index()`:
```python
@bp.route('/')
def index():
    """Root URL — landing page untuk tamu, dashboard untuk yang sudah login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_views.dashboard'))
    return render_template('landing.html')   # sebelumnya: redirect ke login
```

### 3.4 Spesifikasi konten (default yang disarankan)

Section dari atas ke bawah (semua Bahasa Indonesia, ikon Material Symbols):

1. **Navbar (glass, sticky)** — logo ReTrack (light/dark) di kiri; di kanan:
   link "Fitur", tombol **Masuk** (ghost) + **Daftar Gratis** (primary).
   Di mobile: tombol hamburger + menu via Alpine (`x-data`/`x-show`).
2. **Hero** — judul besar (`font-display`), subjudul, dua CTA (Daftar/Masuk),
   latar `--grad-hero` atau ilustrasi/preview dashboard. Tegaskan value:
   "Catat transaksi, atur budget, capai goal — pantau erosi nilai rupiah."
3. **Fitur unggulan (grid 3–6 kartu)** — Transaksi & dompet, Budget per
   kategori, Savings goals, Laporan & grafik, Pantau kurs USD/IDR & emas,
   **Erosi nilai** (fitur khas). Tiap kartu: ikon + judul + 1 kalimat.
4. **(Opsional) Cuplikan dashboard / DWH** — gambar atau mock kartu glass.
5. **CTA penutup** — ajakan daftar + tombol.
6. **Footer** — nama app, tahun, tautan ringkas.

Aksesibilitas: kontras AA (amber → teks gelap), `alt` pada gambar, struktur
heading rapi, fokus terlihat.

### 3.5 Pola teknis (PENTING — landing berdiri sendiri)

Karena landing **tidak** `extends base.html`, salin boilerplate `<head>` dari
`auth/login.html`/`base.html`:
- Preconnect + `<link>` Google Fonts (Plus Jakarta Sans + Space Grotesk).
- `<link>` Material Symbols Outlined.
- Tailwind Play CDN **+ blok `tailwind.config` identik** dengan `base.html`
  (indigo/amber, fontFamily, preflight:false).
- `<link>` `style.css` lalu `custom.css` (pakai `?v={{ asset_v }}` untuk
  cache-busting — `asset_v` sudah disuntik context processor).
- **Skrip anti-FOUC tema** (taruh di `<head>`, sebelum body):
  ```html
  <script>
    (function(){
      var t = localStorage.getItem('refinance-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark':'light');
      if (t === 'dark') document.documentElement.setAttribute('data-theme','dark');
    })();
  </script>
  ```
- Bila ingin toggle dark mode berfungsi penuh, muat `main.js` di akhir body
  (sama seperti base.html) — atau buat toggle kecil sendiri via Alpine.
- Gunakan utility Tailwind dgn warna terkonfigurasi: `bg-primary`,
  `text-primary`, `bg-accent`, `font-display`, `dark:` varian. Untuk
  gradien/glass, pakai variabel CSS yang sudah ada (`var(--grad-hero)`,
  `var(--glass-bg)`) lewat `style="..."` atau kelas baru di `custom.css`.

### 3.6 Test (WAJIB — aturan proyek)

Buat `tests/test_landing.py`. Minimal:
- `GET /` saat **anonim** → `200` dan memuat penanda landing (mis. teks
  "Daftar" / nama produk / tombol CTA).
- `GET /` saat **sudah login** → `302` ke `/dashboard`.
- (opsional) landing memuat tautan ke `/login` dan `/register`.

Pakai fixture `client` di `tests/conftest.py` (TestConfig, DB in-memory).
Jalankan `pytest tests/test_landing.py` lalu `pytest` penuh — **harus tetap
124+ hijau**.

### 3.7 Definition of Done

- [ ] `/` anonim menampilkan landing page yang rapi (terang & gelap).
- [ ] CTA mengarah benar ke `/register` dan `/login`.
- [ ] Responsif (mobile → desktop), menu mobile jalan (Alpine).
- [ ] Tanpa emoji; ikon Material Symbols; copy Bahasa Indonesia.
- [ ] Brand Indigo/Amber + Plus Jakarta Sans/Space Grotesk konsisten.
- [ ] Test landing hijau; seluruh suite tetap hijau.
- [ ] Tidak ada CSS custom di luar `custom.css`.
- [ ] User yang sudah login tetap diarahkan ke dashboard.

### 3.8 Deploy setelah selesai

1. `pytest` (pastikan hijau).
2. Commit + push ke `main`:
   ```bash
   git add app/templates/landing.html app/views/auth_views.py tests/test_landing.py app/static/css/custom.css
   git commit -m "feat: tambah landing page publik di / untuk pengunjung"
   git push
   ```
3. Deploy ke Vercel:
   - **Preview dulu:** `vercel` → cek lewat `vercel curl /ping` /
     `vercel curl /` (preview di belakang Deployment Protection; pakai
     `vercel curl` yang sudah ter-autentikasi — lihat Bagian 4).
   - **Production (minta konfirmasi user):** `vercel --prod`, lalu verifikasi
     `/` dan `/ping` di domain production.
4. Detail langkah deploy lengkap ada di `README.md`.

---

## 4. GOTCHAS / JEBAKAN (yang sudah ditemui sesi ini)

- **CLAUDE.md menyesatkan soal warna/font.** Brand asli = **Indigo `#6366F1` +
  Amber `#F59E0B`**, font **Plus Jakarta Sans + Space Grotesk** (bukan
  teal/pink/Manrope). Ikuti `base.html` & `custom.css`.
- **Landing TIDAK extends base.html.** Harus HTML penuh sendiri (pola
  `auth/login.html`). Jangan lupa skrip anti-FOUC tema di `<head>`.
- **Preview Vercel di belakang Deployment Protection** → `curl` biasa dapat
  **HTTP 401** (halaman "Authentication Required"). Verifikasi pakai
  **`vercel curl <path>`** (otomatis pakai bypass token). Di Git Bash Windows,
  awali dengan **`MSYS_NO_PATHCONV=1`** supaya `/ping` tidak diubah jadi path
  Windows (kalau tidak, error "Malformed input to a URL function").
- **`.env.local` berisi kredensial Neon asli** → gitignored, **jangan commit**.
- **Aset statis dilayani Flask** (vercel.json route `/static/*` → fungsi) →
  `url_for('static', ...)` jalan normal di Vercel. Pakai logo di
  `app/static/img/`, bukan `assets/`.
- **`vercel env add ... preview`** sempat crash (bug CLI v54.7.1). Untuk env
  preview, pakai dashboard bila perlu.
- **Production belum di-deploy** — promosi `vercel --prod` menunggu konfirmasi.
- **Tailwind `preflight: false`** → tidak ada reset bawaan; andalkan
  `style.css` + `custom.css`. Jangan kaget margin/ukuran default berbeda.

---

## 5. KATEGORI CEPAT DI TRANSAKSI + PEMILIH IKON POPUP — ✅ SELESAI (2026-06-03)

> **STATUS: ✅ SELESAI & ter-deploy (sesi 2026-06-03).** Diimplementasi sesuai
> spesifikasi di bawah; `pytest` 137 hijau; di `main` (commit `ab5732f`).
> Lihat ringkasan rilis di **Bagian 7**. Spesifikasi di bawah disimpan sebagai arsip.

> Dua perubahan UX kategori yang diminta user (sesi **2026-06-03**). **Tanpa
> mengubah skema DB, endpoint API, atau fitur dashboard lain.** Dua keputusan
> desain di bawah **SUDAH dikonfirmasi user** — ikuti apa adanya, tidak perlu
> bertanya ulang.

### 5.1 Ringkasan & keputusan (final)

| Fitur | Keputusan user (final) |
|---|---|
| **Fitur 1** — tambah kategori cepat dari dalam form Transaksi | **Ikon default otomatis.** Quick-add cukup minta **nama**; `kind` ikut tipe transaksi yang sedang dipilih; `icon` di-set otomatis ke ikon standar. Ikon bisa diganti nanti di halaman Kategori. Tujuan: akses cepat tanpa pindah halaman. |
| **Fitur 2** — pemilihan ikon di halaman Kategori | **Popup grid ikon kurasi + kotak cari** (mengganti input teks bebas). Tetap sediakan **fallback ketik manual** untuk ikon di luar daftar. |

### 5.2 Konteks kode (titik sentuh — sudah diverifikasi sesi ini)

**API & data — TIDAK perlu diubah (sudah mendukung):**
- `POST /api/categories` body `{name, kind, icon}` → `201 {ok:true, data:{id,name,kind,icon}}` (`app/api/categories.py:23`).
- `api.js` membuka `{ok,data}` → `apiGet('/api/categories')` mengembalikan array kategori; `apiPost(...)` mengembalikan objek kategori (berisi `id`). **Verifikasi unwrap di `app/static/js/api.js`** sebelum dipakai.
- `Category.icon` = `String(50)`, nullable (`app/models/category.py:15`). **Tanpa dedupe nama di server** → cegah duplikat di sisi klien.
- Ikon default yang SUDAH dipakai render daftar (samakan!): income→`payments`, expense→`receipt_long` (`app/templates/categories/index.html:151`).

**Frontend:**
- `app/templates/transactions/index.html`: `<select id="tr-kategori">` (~baris 157) diisi `isiDropdownKategoriForm()` (~baris 252), difilter radio `name="tipe"`; state `semuaKategori` (~baris 186) via `muatKategori()` (~baris 228); simpan transaksi `simpanTransaksi()` (~baris 498).
- `app/templates/categories/index.html`: input ikon teks bebas `#kat-ikon` (~baris 86–91); `simpanKategori()` (~baris 228), `editKategori()` (~baris 191), `bukaModalTambah()` (~baris 178).

### 5.3 Fitur 1 — Quick-add kategori di form Transaksi

**UI:** di samping `<select id="tr-kategori">`, tambah tombol-ikon **"+"** (Material
Symbol `add`, `class="btn-icon"`, target ≥44px). Klik → buka panel kecil inline
(di mobile jadikan bottom-sheet, konsisten pola modal→sheet di `custom.css` §18)
berisi **1 input nama + tombol "Tambah"**. **Tanpa** pemilih ikon di sini (sesuai
keputusan: ikon default otomatis).

**Alur:**
1. `kind` = nilai radio `name="tipe"` yang aktif (income/expense).
2. `name` = isi input (trim; wajib, tampilkan error bila kosong).
3. **Cegah duplikat:** cari di `semuaKategori` — bila ada `name` sama (case-insensitive) + `kind` sama, JANGAN POST; cukup pilih yang sudah ada.
4. `icon` default = `kind === 'income' ? 'payments' : 'receipt_long'`.
5. `POST /api/categories {name, kind, icon}` → terima objek `{id, ...}`.
6. Update state: tambahkan ke `semuaKategori` (atau panggil ulang `muatKategori()`), jalankan `isiDropdownKategoriForm()`, lalu **set `#tr-kategori`.value = id baru** (auto-pilih). Tambahkan juga ke dropdown filter `#filter-kategori`.
7. Tutup panel; tangani error → tampilkan di `#error-modal-transaksi`.

Harus berfungsi baik di mode **tambah** maupun **edit** transaksi (modal yang sama).

### 5.4 Fitur 2 — Popup pemilih ikon di halaman Kategori

Ganti input teks `#kat-ikon` menjadi:
- **Tombol pemicu** menampilkan **preview ikon terpilih** + label ("Pilih ikon").
  Simpan nilai di `<input type="hidden" id="kat-ikon" name="icon">` —
  **pertahankan id/name** agar `simpanKategori()` tetap jalan tanpa diubah.
- Klik pemicu → buka **popup** (reuse pola `.modal-overlay`/`.modal` → otomatis jadi
  bottom-sheet di mobile, atau popover Alpine). Isi popup:
  - **Kotak cari** — filter ikon berdasarkan keyword.
  - **Grid ikon kurasi** (Material Symbols) yang bisa diklik; ikon terpilih di-highlight
    (mis. border / `bg-primary-light`).
  - **Fallback** baris kecil "ketik nama ikon manual" untuk ikon di luar daftar.
- Pilih ikon → set hidden input + preview → tutup popup.
- `editKategori()`: set preview & hidden value dari `kat.icon`.
- `bukaModalTambah()`: reset preview ke ikon default.

**Daftar ikon kurasi (saran awal — boleh disesuaikan; semua Material Symbols
Outlined, JANGAN emoji):**
`restaurant, fastfood, local_cafe, lunch_dining, local_bar, shopping_cart,
shopping_bag, storefront, checkroom, local_mall, directions_bus, directions_car,
local_taxi, train, flight, two_wheeler, local_gas_station, receipt_long, bolt,
water_drop, wifi, home, apartment, cleaning_services, build, medical_services,
local_hospital, fitness_center, medication, movie, sports_esports, music_note,
sports_soccer, travel_explore, school, menu_book, laptop_chromebook, pets,
child_care, volunteer_activism, payments, savings, account_balance, work, paid,
card_giftcard, attach_money, trending_up, redeem, category, label`

### 5.5 File yang diubah

| File | Aksi |
|---|---|
| `app/templates/transactions/index.html` | UBAH — tombol "+" + panel quick-add + JS (POST, dedupe, auto-select) |
| `app/templates/categories/index.html` | UBAH — input teks ikon → tombol+popup (grid+cari+fallback); sesuaikan `simpanKategori`/`editKategori`/`bukaModalTambah` |
| `app/static/css/custom.css` | UBAH (bila perlu) — kelas `.icon-picker*`, grid, highlight; pastikan popup→sheet di ≤768px & target sentuh ≥44px |
| `tests/` | TAMBAH/UBAH — lihat 5.6 |
| `app/api/categories.py`, `app/models/` | **TIDAK diubah** (API & skema sudah cukup) |

### 5.6 Test (WAJIB — aturan proyek)

- Pastikan test API kategori (`tests/test_api_3b.py` dkk) tetap hijau; tambah penegasan `POST /api/categories` menerima `icon` & membalas `id` bila belum tercakup.
- (Bila ada pola test render) cek template transaksi memuat tombol quick-add, dan template kategori memuat struktur picker (hidden `#kat-ikon` + tombol pemicu).
- `pytest` penuh **harus tetap hijau (≥127)**.
- QA manual lebar mobile (≤768px): popup→sheet, tombol ≥44px, input ≥16px (anti auto-zoom iOS).

### 5.7 Definition of Done

- [ ] Dari form Transaksi bisa menambah kategori baru tanpa pindah halaman; langsung terpilih; `kind` ikut tipe transaksi; ikon default otomatis.
- [ ] Quick-add tidak membuat duplikat (nama+tipe sama).
- [ ] Di halaman Kategori, ikon dipilih lewat popup grid + cari (bukan ketik bebas); fallback manual ada; edit menampilkan ikon saat ini.
- [ ] Jalan di desktop & mobile (popup→sheet, ≥44px); tanpa emoji; Material Symbols; UI Bahasa Indonesia.
- [ ] CSS hanya di `custom.css`; reaktivitas via Alpine (bukan jQuery).
- [ ] `pytest` penuh hijau; fitur dashboard lain tak berubah.

### 5.8 Deploy setelah selesai

**Tidak ada perubahan sisi Vercel yang diperlukan** untuk kedua fitur ini —
murni frontend, jadi **tanpa** env var baru, **tanpa** ubah `vercel.json`/build,
**tanpa** migrasi DB Neon, **tanpa** dependency baru. Ini rilis frontend biasa.

1. `pytest` penuh hijau → `git commit` → `git push origin main`.
2. **Pastikan mode deploy dulu** (jangan asumsikan auto-deploy): buka Vercel →
   project `retrack` → **Deployments**. Apakah commit terbaru muncul otomatis
   sebagai deployment baru?
   - **Muncul** → Git Integration aktif; push sudah cukup, tunggu status *Ready*.
   - **Tidak muncul** → Git Integration belum nyala. Deploy manual:
     `vercel --prod` (install CLI dulu bila perlu: `npm i -g vercel`), atau
     sambungkan repo di Settings → Git.
   > Konteks: §1.1 mencatat deploy lama dilakukan **manual** (`vercel deploy`/
   > `vercel --prod`) & production belum tentu otomatis dari `git push`.
3. **Verifikasi** (URL ada di balik Deployment Protection → request anonim dapat
   **401**, itu normal): login browser ke
   `https://retrack-irsyad-hakims-projects.vercel.app` **atau** `vercel curl <path>`
   (lihat Bagian 4 & **`vercel_done.md`**). Catatan: `retrack.vercel.app` polos =
   milik orang lain, **bukan** app ini.

---

## 6. PERBAIKAN MOBILE — MENU PROFIL (AKUN + LOGOUT) DI TOPBAR — ✅ SELESAI (2026-06-03)

> **STATUS: ✅ SELESAI & ter-deploy (sesi 2026-06-03).** Menu profil avatar
> ditambahkan di topbar (Alpine dropdown) pada semua halaman terproteksi;
> commit `ab5732f` di `main`. Lihat **Bagian 7**. Spesifikasi di bawah = arsip.

> Masalah dilaporkan user (sesi **2026-06-03**, terlihat dari Vercel di HP): di
> **mobile TIDAK ada tombol logout maupun jalan ke halaman akun**. Keputusan
> desain **SUDAH dikonfirmasi user**: **menu profil (avatar) di topbar** — ikuti
> apa adanya, tidak perlu bertanya ulang. Murni frontend; tanpa ubah DB/API.

### 6.1 Diagnosis (akar masalah — terverifikasi sesi ini)

- Logout & profil **hanya** ada di dasar halaman Pengaturan
  (`app/templates/settings/index.html:198–205` → `auth_views.logout` = **`GET /logout`**,
  redirect ke `/login`). Halaman Pengaturan = "halaman akun" (profil, ganti
  sandi, ekspor, logout).
- Satu-satunya tautan ke Pengaturan = item di `sidebar-footer`
  (`app/templates/partials/_sidebar.html:82–88`). Di mobile cuma terjangkau lewat
  bottom-nav **"Lainnya"** → drawer (`_bottomnav.html:40–45` → `toggleSidebar()`).
- `.sidebar` (`app/static/css/style.css:112`) pakai `height:100vh; overflow-y:auto`
  **tanpa** padding safe-area. Di mobile footer "Pengaturan" jatuh **di bawah
  viewport** (ketutup chrome browser / bottom-nav `z-index:95`) → sulit/ tak
  terlihat.
- `topbar-right` (`app/templates/base.html:90–96`) **hanya** berisi theme toggle —
  tak ada menu akun/avatar.
- **Akibat:** di mobile, logout & akun praktis tak ketemu.

### 6.2 Keputusan desain (final — dikonfirmasi user)

**Menu profil di topbar.** Tombol **avatar (inisial nama)** di `topbar-right`,
**kiri** dari theme toggle, tampil di **SEMUA** halaman (termasuk mobile). Tap →
dropdown Alpine berisi: **header nama + email**, **"Akun & Pengaturan"** →
`/settings`, **"Keluar"** → `/logout`. Inisial **di-render server-side** via
`current_user` (tanpa fetch tambahan).

### 6.3 Konteks kode (titik sentuh — terverifikasi)

- `app/templates/base.html` → `.topbar-right` (~baris 90–96): tempat menyisipkan
  menu (sebelum `.theme-toggle`).
- `current_user` (Flask-Login) tersedia di template. `User.name` (`String(80)`,
  NOT NULL) & `User.email` ada (`app/models/user.py:12,14`). Inisial =
  `current_user.name[0]|upper`.
- Rute siap pakai: `url_for('auth_views.logout')` = `GET /logout`;
  `url_for('settings_views.settings')` = halaman akun.
- **Alpine.js** sudah dimuat (`base.html:47`). **CSS custom hanya** di
  `app/static/css/custom.css`.
- `base.html` dipakai semua halaman terproteksi (`login_required`) → `current_user`
  pasti authenticated; tetap bungkus `{% if current_user.is_authenticated %}`
  untuk aman.

### 6.4 Implementasi

**HTML** — sisipkan di `base.html` dalam `.topbar-right`, **sebelum** tombol
`.theme-toggle`:

```html
{% if current_user.is_authenticated %}
<div class="profile-menu" x-data="{ open: false }" @keydown.escape="open = false">
  <button type="button" class="profile-avatar-btn" @click="open = !open"
          :aria-expanded="open" aria-haspopup="true" aria-label="Menu akun">
    <span class="profile-avatar">{{ current_user.name[0]|upper }}</span>
    <span class="material-symbols-outlined profile-caret">arrow_drop_down</span>
  </button>
  <div class="profile-dropdown glass-panel" x-show="open" x-transition
       @click.outside="open = false" x-cloak>
    <div class="profile-dropdown-head">
      <div class="profile-dropdown-name">{{ current_user.name }}</div>
      <div class="profile-dropdown-email">{{ current_user.email }}</div>
    </div>
    <a class="profile-dropdown-item" href="{{ url_for('settings_views.settings') }}">
      <span class="material-symbols-outlined">settings</span> Akun &amp; Pengaturan
    </a>
    <a class="profile-dropdown-item profile-dropdown-danger"
       href="{{ url_for('auth_views.logout') }}"
       onclick="return confirm('Yakin ingin keluar?')">
      <span class="material-symbols-outlined">logout</span> Keluar
    </a>
  </div>
</div>
{% endif %}
```

**CSS** (`custom.css`): `.profile-menu{position:relative}`; `.profile-avatar-btn`
(≥44px, flex, gap, bg transparan); `.profile-avatar` (lingkaran ~34px, gradient
`var(--grad-brand)`, teks putih, tebal); `.profile-dropdown`
(`position:absolute; right:0; top:calc(100% + 8px); min-width:208px; z-index:96`
— di atas topbar; radius; shadow; glass-panel); `.profile-dropdown-item`
(flex, gap, padding ≥44px, hover `--bg`); `.profile-dropdown-danger{color:var(--neg)}`;
`.profile-dropdown-head` (nama tebal + email kecil `--text-2`). Tambah
`[x-cloak]{display:none}` global (sekali, bila belum ada). Dark-mode aware.
Pastikan di mobile dropdown **tidak overflow kanan** (`right:0` + `max-width`).

> Logout di halaman Pengaturan **tetap dibiarkan** (tak perlu diubah).

### 6.5 (Opsional) Pengerasan drawer

Bila ringan & tak mengganggu desktop, sekalian cegah cut-off footer drawer:
`.sidebar { height:100dvh }` + `.sidebar-footer { padding-bottom: calc(1rem + var(--safe-bottom)) }`.
**Tidak wajib** — menu topbar sudah menuntaskan masalah.

### 6.6 Test (WAJIB — aturan proyek)

- Tambah/`perluas` test render (mis. `tests/test_navigation.py`): saat **login**,
  halaman terproteksi (mis. `/dashboard`) memuat `class="profile-menu"`,
  `href="/logout"`, dan tautan ke `/settings`. Pakai fixture `client` +
  helper login (lihat `tests/test_fase5.py`).
- `pytest` penuh **tetap hijau**.
- QA manual mobile (≤768px): avatar terlihat tiap halaman; dropdown buka/tutup
  (klik luar & Escape); target ≥44px; tak overflow kanan.

### 6.7 Definition of Done

- [ ] Avatar muncul di topbar **setiap** halaman (mobile & desktop); tap → dropdown.
- [ ] Dropdown punya **"Akun & Pengaturan"** → `/settings` & **"Keluar"** → `/logout` (confirm).
- [ ] Inisial server-render via `current_user`; **tanpa** fetch tambahan.
- [ ] Tanpa emoji; Material Symbols; Alpine (bukan jQuery); CSS hanya di `custom.css`.
- [ ] Test hijau; fitur lain tak berubah.

### 6.8 Urutan kerja & deploy (gabungan Bagian 5 + 6)

Kedua tugas **murni frontend → satu rilis**. Urutan sesuai arahan user:

1. **Fase fitur (Bagian 5):** implementasi quick-add kategori + pemilih ikon popup
   + test → `pytest` hijau → **commit** (mis. `feat(ui): kategori cepat di
   transaksi + pemilih ikon popup`).
2. **Fase mobile (Bagian 6):** implementasi menu profil topbar + test →
   `pytest` hijau → **commit** (mis. `fix(mobile): menu profil akun+logout di
   topbar`).
3. **Deploy Vercel:** ikuti langkah **5.8** (push `main`; cek apakah commit
   muncul otomatis di Deployments; bila tidak, `vercel --prod`; verifikasi via
   login browser / `vercel curl <path>`). **Tanpa** env/migrasi/dependency baru.
   Promosi production = **konfirmasi user** dulu.

---

## 7. STATUS RILIS (sesi 2026-06-03) — Bagian 5 & 6 SELESAI

**Terimplementasi & teruji:**
- Fitur 1 (quick-add kategori di Transaksi), Fitur 2 (pemilih ikon popup di
  Kategori), dan perbaikan mobile (menu profil akun+logout di topbar).
- `pytest` penuh **137 hijau** (127 baseline + 10 test baru:
  `tests/test_ui_kategori.py`, `tests/test_navigation.py`).
- File diubah: `app/templates/{transactions,categories,base}/…`,
  `app/static/css/custom.css` (§19), + 2 test baru.

**Git:** 3 commit di `main` → `ab5732f` (di-push ke
`github.com/irsyadhakimfs-dotdata/retrack`).

**Deploy Vercel — TEMUAN PENTING:** **Git Integration TERNYATA AKTIF.** Push ke
`main` **otomatis** membuat deployment (commit `ab5732f` muncul sendiri di
Deployments). Ini **mengoreksi asumsi §1.1** yang menyebut deploy historis
manual & "production belum tentu otomatis dari git push". Untuk rilis frontend
berikutnya: **cukup `git push origin main`**, lalu tunggu status *Ready*
(production, karena `main` = production branch). Verifikasi tetap via login
browser ke `https://retrack-irsyad-hakims-projects.vercel.app` (request anonim =
401, itu normal).

> Catatan: commit ke-4 (update status doc ini) sengaja **belum di-push** saat
> sesi ditutup agar tak memicu deploy ulang berulang saat verifikasi. Push
> kapan pun bersama perubahan berikutnya.

---

*Disusun pada sesi 2026-06-02 (audit deployment + setup Vercel/Neon).
Diperbarui sesi **2026-06-03**: landing SELESAI; Bagian 5 (kategori cepat +
pemilih ikon) **dan Bagian 6** (perbaikan mobile: menu profil akun+logout) kini
**SELESAI & ter-deploy**; ditambah **Bagian 7** (status rilis + temuan Git
Integration aktif). Perbarui dokumen ini bila status berubah.*
