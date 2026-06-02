# PROGRESS — ReTrack (Agent Handoff Document)

> File ini dibuat untuk memberikan konteks lengkap kepada agent Claude Code baru
> agar bisa langsung melanjutkan pekerjaan tanpa membaca ulang semua history.
> Perbarui file ini setelah tiap perubahan selesai.

---

## Status Proyek

| Item | Status |
|------|--------|
| Fase 1 — Setup (factory, health-check) | ✅ Selesai |
| Fase 2 — Database (semua model + migrasi) | ✅ Selesai |
| Fase 3 — API Backend (CRUD + services) | ✅ Selesai |
| Fase 4 — Frontend (templates + static) | ✅ Selesai |
| Fase 5 — Integrasi & Uji Akhir | ✅ Selesai |
| **Test suite** | ✅ **99 passed** |
| Trend analysis default 6 → 2 bulan (configurable) | ✅ Selesai |
| Perubahan 1 — Rename tampilan → ReTrack | ✅ Selesai |
| Perubahan 2 — Logo ReTrack + favicon | ✅ Selesai |
| Perubahan 3 — Market via yfinance + linechart | ✅ Selesai |
| Perubahan 4 — Sesuaikan web (perlu klarifikasi) | ❓ Tunggu user |

---

## Ringkasan Proyek

**ReTrack** (nama teknis tetap `refinance`) — web personal finance & budget planner
Flask untuk pengguna Indonesia (mahasiswa, fresh grad, pekerja muda 18–30 th).

**Stack:** Python 3.11 · Flask (application factory) · SQLite + SQLAlchemy ·
Flask-Migrate · Flask-Login · Jinja2 · Chart.js · Pytest

**Jalankan:**
```bash
flask run          # dev server
pytest -q          # semua test
```

---

## Aturan Wajib (dari CLAUDE.md — TIDAK BOLEH dilanggar)

1. **Pemisahan lapisan tegas:** `models/` (data only) · `api/` (selalu return JSON `{ok,data}`) · `services/` (logika bisnis murni) · `views/` (render HTML)
2. **Komentar Python pakai `#` Bahasa Indonesia** yang jelas (untuk pemula)
3. **Semua teks UI Bahasa Indonesia**
4. **Warna via CSS variables** — chart pakai `getComputedStyle` agar ikut `data-theme`
5. **Jangan hardcode secret/interval** — pakai `.env` + `app/config.py`
6. **Tulis/perbarui test untuk setiap perubahan perilaku**
7. **Jangan refactor di luar scope** perubahan yang sedang dikerjakan
8. **Nama teknis `refinance` TETAP** (folder package, `refinance.db`, localStorage key `refinance-theme`, import path)

---

## Tiga Keputusan Final (tidak perlu ditawar ulang)

1. **Sumber data market = yfinance.** Tabel `RateHistory`, APScheduler, seed dummy — DIBATALKAN. yfinance menyediakan data historis langsung tanpa API key.
2. **Rename hanya nama tampilan.** Nama teknis `refinance` (folder, DB, import, localStorage key) tetap agar import/migrasi aman.
3. **Commit terpisah per perubahan.**

---

## ✅ Perubahan 1 — SELESAI

**Rename tampilan ReFinance → ReTrack**

File yang diubah (hanya string user-visible):
- `README.md` baris 1: `# ReFinance` → `# ReTrack`
- `app/templates/base.html`: title default + sidebar logo + topbar h1
- `app/templates/auth/login.html`: title + auth-logo text
- `app/templates/auth/register.html`: title + auth-logo text + subtitle
- `app/templates/market/index.html`: teks paragraf erosi nilai

Yang **DIBIARKAN** (nama teknis):
- `app/config.py` → `refinance_dev.db`
- `localStorage.getItem('refinance-theme')` di base.html, login.html, register.html
- `app/api/export.py` → `refinance-export.csv` (lowercase, file unduhan)
- Semua komentar Python/JS/CSS → internal, tidak terlihat user

**Commit yang harus dibuat:**
```
refactor: rename tampilan ReFinance menjadi ReTrack
```
*(Ingatkan user untuk commit ini sebelum lanjut ke Perubahan 2)*

---

## ✅ Perubahan 2 — SELESAI

**Pasang logo ReTrack baru + favicon**

### File yang dibuat/diubah:
- `app/static/img/logo-light.png` — 192×192, hitam, bg transparan (light mode)
- `app/static/img/logo-dark.png` — 192×192, putih, bg transparan (dark mode)
- `app/static/img/logo-32.png` — 32×32, untuk favicon
- `app/static/css/style.css` — tambah class `.logo-light`/`.logo-dark` toggle via `data-theme`
- `app/templates/base.html` — favicon link + sidebar logo pakai `<img>` (dua varian)
- `app/templates/auth/login.html` — auth-logo pakai `<img>` (dua varian)
- `app/templates/auth/register.html` — auth-logo pakai `<img>` (dua varian)

### Solusi dark mode: Solusi A
Dua `<img>` dengan class `.logo-light`/`.logo-dark` di-toggle via CSS `[data-theme="dark"]`.

**Commit yang harus dibuat:**
```
feat: pasang logo ReTrack baru + favicon
```
*(Ingatkan user untuk commit ini sebelum lanjut ke Perubahan 3)*

---

## ✅ Perubahan 3 — SELESAI

**Market via yfinance + linechart kurs USD/IDR 6 bulan**

### File yang diubah:
| File | Perubahan |
|------|-----------|
| `requirements.txt` | tambah `yfinance==0.2.55` |
| `.env.example` | ganti `MARKET_API_KEY` → `MARKET_REFRESH_HOURS=6` |
| `app/config.py` | tambah `MARKET_REFRESH_HOURS` di class `Config` |
| `app/services/market_service.py` | tulis ulang pakai yfinance; tambah `get_usd_idr_history()` |
| `app/api/market.py` | tambah `GET /api/market/usd-idr/history?months=6` |
| `tests/test_api_3d.py` | semua mock diupdate ke `yf.Ticker`; tambah `TestMarketHistory` (3 test) |
| `app/static/js/charts.js` | tambah `initUsdIdrLineChart()` dengan pola cssVar + `_rfCharts` |
| `app/templates/market/index.html` | linechart + kartu emas + auto-refresh `setInterval` |
| `app/views/market_views.py` | kirim `refresh_hours` dari config ke template |

### Hasil test: **99 passed** (naik dari 96 — 3 test baru di TestMarketHistory)

**Commit yang harus dibuat:**
```
feat(market): pindah ke yfinance + linechart kurs 6 bulan auto-update
```

---

## ⏳ Perubahan 4 — BELUM DIKERJAKAN (spesifikasi sudah jelas)

**Integrasi Data Warehouse (Star Schema) + App Polish**

Konteks: Pemilik proyek punya tugas matakuliah Data Warehouse (Universitas Brawijaya).
ReTrack digunakan sebagai topik tugas. Perubahan 4 menambahkan lapisan DWH ke atas
OLTP yang sudah ada.

**Spesifikasi lengkap: `docs/06-perubahan4-dwh.md`** — baca file itu untuk detail teknis penuh.

### Ringkasan sub-fase:

| Sub-fase | Deskripsi | File utama |
|----------|-----------|-----------|
| **4a** | Model DWH (dim + fact SQLAlchemy) | `app/models/dwh.py` + migrasi |
| **4b** | ETL Service (extract→transform→load) | `app/services/etl_service.py` |
| **4c** | API endpoint DWH (run ETL, query DWH) | `app/api/dwh.py` |
| **4d** | Halaman DWH Dashboard (chart + screenshot untuk PPT) | `app/views/dwh_views.py` + `app/templates/dwh/` |
| **4e** | Test | `tests/test_dwh.py` |

### Schema DWH (Star Schema):
- **Fakta:** `dwh_fact_transaction` (amount, kind, usd_rate_at_date, erosi_persen)
- **Dimensi:** `dwh_dim_date` · `dwh_dim_user` · `dwh_dim_wallet` · `dwh_dim_category`
- Semua tabel DWH disimpan di DB yang sama (`refinance_dev.db`) dengan prefix `dwh_`

### Commit setelah selesai:
```
feat(dwh): tambah lapisan data warehouse star schema + ETL + dashboard
```

---

## Perubahan Tambahan yang Sudah Selesai (di luar 4 perubahan utama)

- **Trend analysis default diubah 6 → 2 bulan** (via `TREND_DEFAULT_MONTHS` di config)
  - File: `app/config.py`, `app/api/reports.py`, `.env.example`
  - Bisa diubah: set `TREND_DEFAULT_MONTHS=N` di `.env` (1–6 bulan)
  - Endpoint masih menerima `?months=N` untuk override manual

---

## Cara Melanjutkan (untuk agent baru)

1. Baca file ini
2. Baca `CLAUDE.md` (aturan pengembangan)
3. Baca `docs/05-perubahan-retrack.md` (spesifikasi detail lengkap)
4. Cek apakah Perubahan 1 sudah di-commit (`git log --oneline -5`)
5. Jika belum → ingatkan user untuk commit dulu
6. Lanjutkan ke **Perubahan 2** (logo), ikuti langkah di atas
7. Setelah tiap perubahan: jalankan `pytest -q`, laporkan hasil, ingatkan user commit
8. **Jangan commit otomatis** kecuali diminta user

**File kunci yang akan disentuh tiap perubahan:**

| Perubahan | File utama |
|-----------|-----------|
| 4a (model) | `app/models/dwh.py` · `app/models/__init__.py` · migrasi baru |
| 4b (ETL) | `app/services/etl_service.py` |
| 4c (API) | `app/api/dwh.py` · `app/api/__init__.py` |
| 4d (frontend) | `app/views/dwh_views.py` · `app/templates/dwh/dashboard.html` · `app/templates/base.html` |
| 4e (test) | `tests/test_dwh.py` |

**Baca `docs/06-perubahan4-dwh.md` untuk spesifikasi lengkap Perubahan 4.**
