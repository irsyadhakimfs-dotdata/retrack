# ReFinance (ReTrack)

Web personal **financial & budget planner** untuk pengguna Indonesia (mahasiswa,
fresh graduate, pekerja muda 18–30 th): mencatat transaksi, mengatur budget,
menabung untuk goal, memantau kurs USD/IDR & harga emas, mendeteksi pemborosan,
serta dashboard **Data Warehouse (star schema)** untuk analisis.

## Fitur Utama
- Pencatatan transaksi pemasukan & pengeluaran
- Budget bulanan per kategori
- Multiple wallets / rekening
- Savings goals
- Laporan & grafik (Chart.js)
- Pemantauan kurs USD/IDR & harga emas
- **Erosi nilai** — tampilkan % daya beli yang tergerus perubahan kurs
- **Dashboard DWH** — star schema (`dwh_*`) yang di-load oleh ETL service

## Stack

- **Backend:** Python 3.11, Flask (application factory), SQLAlchemy ORM, Flask-Migrate, Flask-Login
- **Database:** SQLite (lokal/dev) · PostgreSQL (produksi/Vercel)
- **Frontend:** Tailwind CSS (Play CDN) + Alpine.js + Chart.js + Material Symbols (tanpa build step)
- **Data eksternal:** kurs USD/IDR & emas via `yfinance` (lokal) dengan fallback HTTP gratis
  (`open.er-api` / `frankfurter` / `gold-api`) — fallback inilah yang dipakai di Vercel.

> **Catatan DWH:** "Data Warehouse" di proyek ini adalah sekumpulan tabel
> `dwh_*` (star schema) di **database yang sama**, di-load oleh ETL service.
> Tidak ada DuckDB maupun file model `.pth` — proyek ini murni Flask + SQL.

---

## Menjalankan secara lokal

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell: .venv\Scripts\Activate.ps1)
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements-dev.txt   # full stack (termasuk yfinance + pytest)

copy .env.example .env                # lalu isi SECRET_KEY
flask --app run db upgrade            # buat skema dari migrasi
flask --app run run                   # http://127.0.0.1:5000/ping
```

Menjalankan test:

```bash
pytest                 # semua test (124)
pytest tests/test_models.py
```

---

## Deploy ke Vercel

Aplikasi ini berjalan di Vercel sebagai **serverless function** (`@vercel/python`).
File kunci sudah disiapkan: `api/index.py` (entrypoint WSGI), `vercel.json`,
`requirements.txt` (ramping, tanpa yfinance).

### ⚠️ Wajib dibaca dulu: database

Filesystem Vercel **read-only** (kecuali `/tmp` yang efemeral). Artinya **SQLite
tidak persisten** — semua tulisan (login, transaksi, ETL) hilang tiap invocation.
Karena itu produksi **wajib** memakai PostgreSQL eksternal:

- [Neon](https://neon.tech) (gratis), atau
- **Vercel Postgres** (Storage tab di dashboard), atau Supabase.

### Langkah deploy

**1. Push ke GitHub**

```bash
git add .
git commit -m "chore: siapkan deployment Vercel (entrypoint, config Postgres, requirements ramping)"
git branch -M main
git remote add origin https://github.com/irsyadhakimfs-dotdata/retrack.git
git push -u origin main
```

**2. Siapkan database Postgres** — buat database (Neon/Vercel Postgres), salin
connection string (mis. `postgresql://user:pass@host/db?sslmode=require`).

**3. Import project di Vercel** — [vercel.com/new](https://vercel.com/new) →
pilih repo. Framework Preset: **Other** (vercel.json sudah mengatur build).

**4. Set Environment Variables** (Settings → Environment Variables):

| Key             | Value                          | Catatan                              |
| --------------- | ------------------------------ | ------------------------------------ |
| `FLASK_ENV`     | `production`                   | wajib                                |
| `SECRET_KEY`    | string acak panjang            | wajib — jangan pakai default         |
| `DATABASE_URL`  | connection string Postgres     | wajib                                |
| `AUTO_CREATE_DB`| `1`                            | buat tabel otomatis saat cold start  |

**5. Deploy.** Saat cold start pertama, `db.create_all()` membuat seluruh tabel
(OLTP + `dwh_*`) di Postgres. Buka URL `.vercel.app`, cek `/ping` → `{"ok": true}`.

### Lewat Vercel CLI (alternatif)

```bash
npm i -g vercel
vercel            # preview
vercel --prod     # production
```

### Migrasi (opsional, ganti AUTO_CREATE_DB)

Untuk skema yang dikelola Alembic alih-alih `create_all`, jalankan dari lokal
dengan `DATABASE_URL` mengarah ke Postgres produksi:

```bash
set DATABASE_URL=postgresql://...        # Windows
flask --app run db upgrade
```

lalu set `AUTO_CREATE_DB=0` di Vercel.

---

## Struktur proyek

```
app/
  __init__.py        # create_app() — application factory
  config.py          # Dev / Test / Prod (normalisasi URL Postgres)
  extensions.py      # db, migrate, login_manager
  models/            # tabel OLTP + dwh_* (star schema)
  api/               # endpoint REST (JSON)
  services/          # logika bisnis (budget, erosi, market, ETL, report)
  views/             # render template HTML
  templates/ static/ # Jinja2 + CSS/JS
api/index.py         # entrypoint Vercel (WSGI)
vercel.json          # konfigurasi serverless + routing
requirements.txt     # runtime produksi (ramping)
requirements-dev.txt # full stack dev (yfinance, pytest)
migrations/          # Flask-Migrate / Alembic
tests/               # 124 test (pytest)
```
