# CLAUDE.md - Instruksi untuk Claude Code

> **File ini dibaca otomatis oleh Claude Code di setiap sesi. Berisi konteks proyek, aturan ketat, dan konvensi yang harus dipatuhi.**

---

## Identitas Proyek

**Nama:** ReTrack  
**Jenis:** Web Application (Flask, Python)  
**Tujuan:** Personal finance tracker dengan OCR struk via Gemini AI dan market overview kurs USD/IDR  
**Owner:** Mahasiswa Data Science yang sedang belajar web/mobile app development

---

## Stack (FIXED — JANGAN DIGANTI TANPA IZIN)

- **Backend:** Flask 3.x, Python 3.11+
- **ORM:** SQLAlchemy 2.x + Flask-SQLAlchemy
- **Migration:** Flask-Migrate (Alembic)
- **Database:** SQLite (dev), siap migrasi ke PostgreSQL
- **Auth:** Flask-Login + Flask-Bcrypt
- **Forms:** Flask-WTF + WTForms (CSRF wajib aktif)
- **Frontend:** Jinja2 + Tailwind CSS (CDN dulu) + Alpine.js 3.x
- **Charts:** Chart.js 4.x
- **OCR:** Google Gemini API via `google-generativeai`
- **Forex:** `yfinance` (Yahoo Finance)
- **Export:** `pandas` + `openpyxl`

JANGAN install React, Vue, atau framework JS lain. JANGAN setup Webpack/Vite. JANGAN ganti SQLite ke MongoDB.

---

## Struktur Folder (PATUHI)

```
ReTrack/
├── app/
│   ├── __init__.py            # create_app() factory
│   ├── config.py
│   ├── extensions.py          # db, login_manager, migrate, bcrypt, csrf
│   ├── models/                # Satu file per model utama
│   ├── blueprints/            # auth, main, dashboard, financial, wallets, plans, market
│   ├── services/              # gemini_ocr, forex, analytics, exporter
│   ├── static/                # img, css, js, uploads (uploads gitignored)
│   ├── templates/             # base.html + per-blueprint folders
│   └── utils/
├── migrations/
├── tests/
├── instance/                  # SQLite db (gitignored)
├── .env                       # GITIGNORED
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

Pakai **App Factory pattern** (`create_app(config_name)`). JANGAN bikin app monolitik di satu file kecuali `run.py`.

---

## Aturan Coding (HARD RULES)

### Python
1. **Decimal untuk uang.** Gunakan `from decimal import Decimal` dan kolom `db.Numeric(15, 2)`. JANGAN PERNAH gunakan `float` untuk amount/balance.
2. **Type hints** untuk semua function signatures di `services/` dan `utils/`.
3. **Docstrings** untuk semua fungsi public (Google style).
4. **F-strings** untuk formatting, BUKAN `%` atau `.format()`.
5. **Imports** terurut: stdlib → third-party → local. Gunakan `isort` style.
6. **Tidak ada `print()`** di production code. Gunakan `current_app.logger`.

### Flask
1. **Selalu pakai blueprint.** Tidak ada route langsung di `app/__init__.py`.
2. **Validasi form via Flask-WTF**, bukan request.form parsing manual.
3. **CSRF wajib aktif** untuk semua POST/PUT/DELETE.
4. **User isolation:** SETIAP query yang melibatkan data user WAJIB filter `user_id == current_user.id`. JANGAN sampai user A bisa lihat data user B.
5. **`@login_required`** untuk semua route kecuali landing, auth, dan static.
6. **Flash messages** untuk feedback user, kategori: `success`, `error`, `warning`, `info`.

### Database
1. **Migrations untuk SEMUA perubahan schema.** Workflow:
   ```bash
   flask db migrate -m "deskripsi perubahan"
   # REVIEW file migration yang di-generate
   flask db upgrade
   ```
2. **Tidak ada `db.create_all()`** di production. Hanya boleh dipakai untuk testing terisolasi.
3. **Foreign keys eksplisit** dengan `ondelete='CASCADE'` atau `'SET NULL'` sesuai konteks.
4. **Index** kolom yang sering di-query: `user_id`, `transaction_date`, `wallet_id`.
5. **Timestamps:** semua tabel punya `created_at`, tabel yang bisa diedit punya `updated_at`.

### Frontend
1. **Tailwind utility-first.** Kalau bisa pakai utility, jangan bikin custom CSS.
2. **Custom CSS hanya di `static/css/custom.css`** — untuk glassmorphism, animasi, override Tailwind.
3. **Alpine.js untuk reaktivitas.** `x-data`, `x-show`, `x-on`, `x-model`. JANGAN pakai jQuery.
4. **Chart.js untuk SEMUA chart.** Inisialisasi di `static/js/charts.js` atau inline `<script>` di template.
5. **Material Symbols Outlined** untuk ikon. JANGAN PAKAI EMOJI (kesan AI).
6. **Setiap halaman extends `base.html`** kecuali landing.
7. **Sidebar component** di `templates/partials/_sidebar.html`, di-include hanya di halaman yang perlu (Dashboard, Financial Report, Wallets, Plans, Market Overview).

### Glassmorphism (WAJIB di mayoritas card)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
}
```

### Palet Warna (CSS variables di `:root`)
```
--primary: #66BFBF
--primary-light: #EAF6F6
--bg-white: #FCFEFE
--accent: #F76B8A
```
Boleh tambah variasi (lighter/darker shades), tapi JANGAN pakai warna acak.

---

## Keamanan (NON-NEGOTIABLE)

1. **JANGAN PERNAH** commit `.env`, API keys, atau secrets ke git.
2. **JANGAN PERNAH** print/log API keys atau password.
3. **JANGAN PERNAH** bypass `@login_required` untuk "kemudahan testing".
4. **JANGAN PERNAH** trust user input. Validate, sanitize, escape.
5. **File upload:**
   - Whitelist extension: `.jpg`, `.jpeg`, `.png`, `.webp` only
   - Max size: 5MB
   - Validasi dengan Pillow (`Image.open().verify()`)
   - Simpan dengan nama random (UUID), bukan nama asli
6. **Password:** bcrypt cost factor 12, minimum 8 karakter.

---

## Workflow Pengerjaan

1. **Sebelum coding fitur baru**, baca dulu `docs/00-overview.md` dan dokumen relevan di `docs/`.
2. **Phase-by-phase**, jangan loncat. Selesaikan satu phase sebelum lanjut.
3. **Test manual** di browser setiap selesai 1 endpoint/halaman.
4. **Commit per fitur kecil** dengan pesan konvensional:
   - `feat: add wallet CRUD`
   - `fix: correct balance calculation`
   - `refactor: extract analytics to service`
   - `style: glassmorphism on dashboard cards`
5. **Update dokumentasi** kalau ada keputusan arsitektural baru.

---

## Aturan Saat Berinteraksi dengan User

1. **Tanya sebelum asumsi.** Kalau spek ambigu, tanya — jangan tebak.
2. **Tunjukkan diff** sebelum apply perubahan besar.
3. **Jelaskan trade-off** kalau ada beberapa cara melakukan sesuatu.
4. **Bahasa Indonesia** untuk komunikasi, **English** untuk code, comments, dan commit messages.
5. **Berikan langkah verifikasi** setelah selesai (e.g. "test dengan klik X, lalu cek Y").

---

## Yang HARUS Dihindari

- ❌ Membuat fitur yang tidak diminta ("scope creep")
- ❌ Refactor besar-besaran tanpa diminta
- ❌ Mengganti library yang sudah ditetapkan
- ❌ Pakai emoji di UI
- ❌ Float untuk uang
- ❌ Raw SQL string dengan concat user input
- ❌ Bikin endpoint tanpa `@login_required` (kecuali memang public)
- ❌ Lupa filter `user_id` di query
- ❌ Hardcode credentials atau API keys

---

## Referensi Dokumentasi Internal

Selalu baca dokumen ini sesuai konteks:

- `docs/00-overview.md` — Big picture
- `docs/01-architecture.md` — Arsitektur teknis
- `docs/02-database-schema.md` — Model & ERD
- `docs/03-features-spec.md` — Spek fitur per halaman
- `docs/04-design-system.md` — Warna, glass, komponen
- `docs/05-gemini-ocr-integration.md` — Detail OCR
- `docs/06-forex-integration.md` — yfinance setup
- `docs/07-deployment.md` — Deploy guide (Phase 6)

---

## Saat Dalam Keraguan

Tanya user dengan format:
> "Saya menemukan ambiguitas di [X]. Ada 2 pendekatan:
> - **Opsi A:** [...] (trade-off: [...])
> - **Opsi B:** [...] (trade-off: [...])
> 
> Mana yang Anda preferensikan?"

JANGAN diam-diam pilih sendiri.
