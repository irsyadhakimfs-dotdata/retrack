# ReFinance — Konteks Proyek untuk Claude Code

> Baca file ini setiap awal sesi. Ini sumber kebenaran utama proyek.

## Tentang
Web personal financial & budget planner untuk pengguna Indonesia (mahasiswa,
fresh graduate, pekerja muda 18-30 th): mencatat transaksi, mengatur budget,
menabung untuk goal, memantau kurs USD/IDR & emas, dan mendeteksi pemborosan.

## Stack Teknologi
Python 3.11, Flask (pola application factory), SQLite + SQLAlchemy ORM,
Flask-Migrate, Flask-Login (hash werkzeug), Jinja2 + HTML, Pytest.
**Frontend:** Tailwind CSS (Play CDN, utility-first) + Alpine.js (reaktivitas) +
Chart.js (semua grafik) + Material Symbols (ikon). API eksternal: kurs USD/IDR
& harga emas (yfinance, dengan fallback HTTP gratis open.er-api/frankfurter/gold-api).

## Aturan Pengembangan (WAJIB)
1. Pola application factory: `create_app()` di `app/__init__.py`.
2. Pisahkan lapisan dengan TEGAS:
   - `models/`  → hanya definisi tabel (data), tanpa logika tampilan.
   - `api/`     → endpoint REST, SELALU return JSON.
   - `services/`→ logika bisnis murni (budget, laporan, erosi, market).
   - `views/`   → render template HTML.
3. Jangan ubah file di luar scope fase yang sedang dikerjakan.
4. Tulis test untuk SETIAP fitur baru di `tests/`.
5. Komentar kode Python pakai `#` Bahasa Indonesia yang jelas (untuk pemula).
6. UI Bahasa Indonesia. Jangan hardcode secret; pakai `.env` + `app/config.py`.

## Aspek Desain (sistem baru — glassmorphism teal/pink)
Font **Manrope** (Google Fonts). Dark mode via atribut `data-theme="dark"` di
`<html>` (Tailwind `darkMode: ['selector','[data-theme="dark"]']`).

**Aturan frontend (WAJIB):**
1. **Tailwind utility-first.** Jika bisa pakai utility, jangan tulis CSS custom.
2. **CSS custom HANYA di `static/css/custom.css`** — glassmorphism, animasi,
   override Tailwind/legacy, dan definisi CSS variables palet.
   (`style.css` legacy masih dimuat & di-re-tema oleh `custom.css`.)
3. **Alpine.js untuk reaktivitas** (`x-data`, `x-show`, `x-on`, `x-model`).
   JANGAN pakai jQuery.
4. **Chart.js untuk SEMUA chart** — inisialisasi di `static/js/charts.js` atau
   inline `<script>` di template.
5. **Material Symbols Outlined** untuk ikon. JANGAN pakai emoji (kesan AI).
6. Setiap halaman `extends base.html` (kecuali landing).
7. **Sidebar** = komponen di `templates/partials/_sidebar.html`, di-include di
   `base.html`.

**Glassmorphism** (wajib di mayoritas card) → kelas `.glass-card` / `.glass-panel`
di `custom.css` (`backdrop-filter: blur(20px)`, border tipis, radius 16px).

**Palet (CSS variables di `:root`, `custom.css`):**
`--primary: #66BFBF`, `--primary-light: #EAF6F6`, `--bg-white: #FCFEFE`,
`--accent: #F76B8A`. Teal = brand (nav aktif, tombol primary, link, fokus);
pink = aksen/pop. Income `--pos`, expense `--neg`. Boleh tambah shade
(lighter/darker), JANGAN warna acak. Konfigurasi Tailwind ada di `base.html`
(`tailwind.config` → `colors.primary`, `colors.accent`).

## Cara Menjalankan
```bash
flask run                      # mode dev
pytest                         # semua test
pytest tests/test_models.py    # satu file
```

## Fase Pengembangan (bottom-up, testing per fase)
1. Fase 1 — Setup: struktur folder, venv, application factory, health-check.
2. Fase 2 — Database: semua model + migrasi + test_models.
3. Fase 3 — API Backend: endpoint CRUD + services + test API.
4. Fase 4 — Frontend: template & static sesuai desain Stitch.
5. Fase 5 — Integrasi & Uji Akhir: sambung FE-BE, grafik, export CSV, market.

**Fitur Erosi Nilai (hover % daya beli tergerus kurs) = bagian MVP**, terjalin
di Fase 2 (kolom kurs), Fase 3d (service+API+test), Fase 4c (elemen UI hover),
dan Fase 5 (aktivasi penuh). Lihat `docs/04-fitur-erosi-nilai.md`.

**Aturan emas:** fase berikutnya HANYA dimulai setelah fase sekarang lulus uji
(Definition of Done di `docs/00-overview.md`) dan sudah di-commit ke Git.
