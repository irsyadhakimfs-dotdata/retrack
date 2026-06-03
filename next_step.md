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

## 3. TUGAS BERIKUTNYA: LANDING PAGE

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

*Disusun pada sesi 2026-06-02 (audit deployment + setup Vercel/Neon). Perbarui
dokumen ini bila status berubah.*
