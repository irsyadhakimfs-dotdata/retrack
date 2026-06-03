# vercel_done.md — Runbook Deployment Vercel (ReTrack / ReFinance)

> **Untuk siapa dokumen ini?** Diri Anda di masa depan **dan** sesi agent Claude Code
> berikutnya. Isinya: cara kerja deployment, daftar environment variable, info
> database Neon, dan cara **mengedit / men-deploy ulang** project yang sudah ada
> di Vercel. **Tidak berisi nilai secret** (semua secret ada di dashboard Vercel /
> Neon dan di `.env.local` yang di-gitignore). Terakhir diperbarui: **2026-06-03**.

---

## 0. TL;DR untuk sesi berikutnya

- Stack: **Flask (Python) → Vercel sebagai serverless function** (`@vercel/python`).
- Entrypoint Vercel: **`api/index.py`** (bungkus `create_app("production")`).
- Routing: semua request → fungsi (lihat `vercel.json`). Static dilayani Flask.
- DB produksi: **Neon Postgres** (integrasi Vercel Marketplace, env var auto-inject).
- **Cara deploy ulang setelah edit kode → cukup `git push origin main`** (auto-deploy
  via integrasi GitHub). Tidak perlu setting ulang apa pun.
- **JANGAN** commit `.env.local` / `.env` (berisi password DB & SECRET_KEY asli).
- **JANGAN** pakai SQLite di produksi — filesystem Vercel read-only.

---

## 1. Identitas project (non-rahasia, aman disimpan)

| Item | Nilai |
|---|---|
| Nama project Vercel | `retrack` |
| Vercel Project ID | `prj_0z2xk4AfgO5PCDypO6t4MqRkacUr` |
| Vercel Team/Org ID | `team_XxjfqbzwDQk11ic5USxTQbEx` |
| GitHub repo | `https://github.com/irsyadhakimfs-dotdata/retrack.git` (remote `origin`) |
| Branch produksi | `main` |
| Database | Neon Postgres (lihat `NEON_PROJECT_ID` di `.env.local`) |

Sumber: `.vercel/repo.json`. Folder `.vercel/` di-gitignore (jangan di-commit).

---

## 2. Cara kerja deployment (arsitektur)

```
request  ─►  vercel.json route "/(.*)"  ─►  api/index.py  ─►  create_app("production")
                                                              ├─ Flask WSGI app  ► views/api/static
                                                              └─ db.create_all() saat cold start (di-guard)
```

File kunci:
- **`api/index.py`** — entrypoint. Memaksa `FLASK_ENV=production`, baca `DATABASE_URL`
  & `SECRET_KEY` dari env Vercel. Jika `AUTO_CREATE_DB=1`, jalankan `db.create_all()`
  sekali tiap cold start (idempoten — hanya buat tabel yang belum ada, tidak hapus data).
- **`vercel.json`** — `@vercel/python` builder + satu route catch-all ke `api/index.py`.
- **`requirements.txt`** — dependency RUNTIME (ramping, **tanpa** yfinance/pandas).
- **`.vercelignore`** — kecualikan docs/dwh/tests/csv/migrations dari bundle (cold start cepat).
- **`app/config.py`** — `ProdConfig` menormalkan `postgres://`→`postgresql://` dan
  menambah `pool_pre_ping` + `pool_recycle=280` (anti error koneksi idle Neon).

Penting:
- **yfinance opsional** — di Vercel tidak terpasang; `market_service.py` otomatis
  fallback ke API HTTP gratis. Jangan tambahkan yfinance/pandas ke `requirements.txt`
  (membengkak > batas ukuran & memperlambat cold start).
- **Tidak ada tulisan ke disk** (export CSV pakai `io.StringIO`). Aman untuk FS read-only.

---

## 3. Environment Variables

Lokasi pengaturan: **Vercel Dashboard → Project `retrack` → Settings → Environment Variables**.
Salinan lokal ada di `.env.local` (hasil `vercel env pull`, **gitignored**).

### 3a. Dipakai langsung oleh aplikasi (WAJIB ada di Production)

| Key | Fungsi | Catatan |
|---|---|---|
| `DATABASE_URL` | URI Postgres yang dibaca `ProdConfig` | **Wajib pakai endpoint Neon POOLED** (host mengandung `-pooler`) + `?sslmode=require` |
| `SECRET_KEY` | Tanda tangan sesi Flask-Login | String acak panjang; jangan biarkan default `"ganti-di-production"` |
| `FLASK_ENV` | Pilih config | Set `production` |
| `AUTO_CREATE_DB` | `1` → `create_all()` saat cold start | Set `0` jika mengelola skema via migrasi Alembic |

### 3b. Di-inject otomatis oleh integrasi Neon (tersedia, app tak wajib pakai langsung)

`DATABASE_URL_UNPOOLED`, `POSTGRES_URL`, `POSTGRES_URL_NON_POOLING`, `POSTGRES_PRISMA_URL`,
`POSTGRES_URL_NO_SSL`, `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_DATABASE`, `PGHOST`, `PGHOST_UNPOOLED`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`,
`NEON_PROJECT_ID`.

- Yang `*_UNPOOLED` / `*_NON_POOLING` = **koneksi langsung** (pakai untuk migrasi/operasi DDL berat dari lokal).
- Yang lain pooled / varian untuk ORM lain (Prisma dll) — tidak dipakai proyek ini.

### 3c. Otomatis dari platform (abaikan, jangan diutak-atik)

`VERCEL_OIDC_TOKEN` (token OIDC, regen otomatis), `NEON_AUTH_BASE_URL`,
`VITE_NEON_AUTH_URL` (fitur Neon Auth — tidak dipakai aplikasi Flask ini).

> ⚠️ **Nilai asli semua key di atas TIDAK ditulis di file ini.** Ambil dari:
> Vercel Dashboard (Settings → Environment Variables) atau `vercel env pull` → `.env.local`.

---

## 4. Database (Neon Postgres)

- Provider: **Neon**, terpasang via **Vercel Marketplace integration** (bukan Vercel
  Postgres lama). Itulah kenapa env var `POSTGRES_*` / `NEON_*` muncul otomatis.
- **Pooled vs Unpooled:**
  - Aplikasi (serverless, banyak koneksi pendek) → **pooled** (`DATABASE_URL`, host `-pooler`).
  - Migrasi / DDL dari lokal → **unpooled** (`DATABASE_URL_UNPOOLED`).
- Skema dibuat otomatis oleh `db.create_all()` (karena `AUTO_CREATE_DB=1`) — mencakup
  tabel OLTP + tabel `dwh_*` (star schema).
- **Reset/buka dashboard Neon:** [console.neon.tech](https://console.neon.tech) →
  pilih project (lihat `NEON_PROJECT_ID`) → tab Connection Details untuk string baru,
  atau SQL Editor untuk inspeksi data.

### Menjalankan migrasi Alembic ke DB produksi (opsional, ganti AUTO_CREATE_DB)

```powershell
# dari mesin lokal, arahkan ke koneksi UNPOOLED Neon
$env:DATABASE_URL = "postgresql://<user>:<pass>@<host-unpooled>/<db>?sslmode=require"
flask --app run db upgrade
```
Lalu set `AUTO_CREATE_DB=0` di Vercel agar tidak dobel dengan `create_all()`.

---

## 5. MENGEDIT / DEPLOY ULANG project yang sudah ada di Vercel

### 5a. Skenario paling umum: ubah kode lalu rilis

Karena repo GitHub `retrack` terhubung ke project Vercel, **push = deploy**:

```powershell
git add -A
git commit -m "feat/fix: <ringkasan perubahan>"
git push origin main          # → memicu Production Deployment otomatis
```

- Push ke `main` → **Production**.
- Push ke branch lain / buka PR → **Preview Deployment** (URL unik, tidak menyentuh produksi).
- Pantau progres: Vercel Dashboard → Deployments, atau `vercel ls` / `vercel inspect`.

### 5b. Mengubah Environment Variable

**Via Dashboard (paling mudah):** Settings → Environment Variables → edit/add →
pilih environment (Production/Preview/Development) → **Save** → **Redeploy** agar
nilai baru terpakai (env var hanya termuat saat build/deploy baru).

**Via CLI:**
```powershell
vercel env ls                         # lihat daftar (nama saja)
vercel env add NAMA_VAR production    # tambah/timpa (akan diminta nilainya)
vercel env rm NAMA_VAR production     # hapus
vercel env pull .env.local            # tarik semua ke lokal (regen .env.local)
```

### 5c. Rollback ke versi sebelumnya

Dashboard → Deployments → pilih deployment lama yang sehat → **⋯ → Promote to
Production** (atau **Instant Rollback**). Tidak perlu re-build.

### 5d. Re-link kalau folder `.vercel/` hilang

```powershell
npm i -g vercel        # jika belum ada (saat ini CLI BELUM terpasang di mesin ini)
vercel login
vercel link            # pilih team "retrack" org & project "retrack"
```

---

## 6. Vercel CLI — cheat sheet

> Status mesin ini: **Vercel CLI belum terpasang.** Install dulu: `npm i -g vercel`.

```powershell
vercel                 # deploy PREVIEW dari folder saat ini
vercel --prod          # deploy PRODUCTION langsung dari lokal (tanpa lewat git)
vercel ls              # daftar deployment terbaru
vercel logs <url>      # runtime logs (debug 500 / error)
vercel inspect <url>   # detail satu deployment
vercel env pull        # sinkron env Vercel → .env.local
vercel pull            # tarik settings project + env
```

---

## 7. Pengembangan lokal (mirror produksi)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt   # full (yfinance + pytest)
copy .env.example .env                # isi SECRET_KEY untuk dev
python run.py                         # http://127.0.0.1:5000/ping
python -m pytest -q                   # suite penuh → 127 passed (~3 mnt)
```
- Dev default pakai **SQLite** (`instance/refinance_dev.db`) bila `DATABASE_URL` kosong.
- Untuk uji terhadap Postgres asli: `vercel env pull .env.local` lalu jalankan dengan
  `DATABASE_URL` dari situ.

---

## 8. Troubleshooting (gejala → sebab → solusi)

| Gejala | Sebab paling mungkin | Solusi |
|---|---|---|
| `/ping` OK tapi login/transaksi tidak tersimpan | `DATABASE_URL` kosong → fallback SQLite di FS read-only | Set `DATABASE_URL` (pooled) di Vercel, redeploy |
| 500 di semua halaman | `SECRET_KEY` tidak ter-set / import gagal | Cek `vercel logs`; pastikan env var ada |
| Error "server closed the connection unexpectedly" / "too many connections" | Pakai endpoint Neon non-pooled / pool habis | Ganti `DATABASE_URL` ke host `-pooler` (sudah ada `pool_pre_ping`/`pool_recycle`) |
| `TemplateNotFound` / 404 static | template/static tak ikut bundle | Pastikan `.vercelignore` TIDAK mengecualikan `app/` (sudah benar saat ini) |
| Cold start lambat / build gagal "size limit" | dependency berat masuk `requirements.txt` | Jaga `requirements.txt` ramping; yfinance/pandas hanya di `requirements-dev.txt` |
| Env var baru tidak terbaca | belum redeploy setelah ubah | Redeploy / push commit baru |
| Data market kosong | yfinance absen + API gratis kena rate-limit | Normal; akan pulih (ada cache + multi-fallback HTTP) |

Tempat lihat error runtime: **Dashboard → Deployments → (pilih) → Functions / Runtime Logs**, atau `vercel logs <deployment-url>`.

---

## 9. Aturan keamanan (WAJIB diingat agent berikutnya)

- **JANGAN** commit `.env`, `.env.local`, atau folder `.vercel/` (semua sudah di `.gitignore`).
- `.env.example` **boleh** di-commit (template tanpa nilai) — sudah dikecualikan eksplisit
  di `.gitignore` (`!.env.example`).
- **JANGAN** menuliskan connection string Postgres, password, `SECRET_KEY`, atau
  `VERCEL_OIDC_TOKEN` ke file mana pun yang di-commit (termasuk dokumen ini).
- Kalau secret pernah ter-commit tak sengaja: rotasi (Neon: reset password DB; Vercel:
  ganti `SECRET_KEY`) lalu redeploy.

---

## 10. Catatan untuk sesi agent Claude Code berikutnya

- Proyek **sudah audit-ready & deploy-ready** per 2026-06-03 (lihat `MOBILE_LOG_UPDATE.md`
  & `LOG_UPDATE.md`). Suite hijau: **127 passed**.
- Tata letak **mobile** (bottom-nav, tabel→kartu, modal→sheet, filter→sheet, safe-area)
  sudah diimplementasi & diverifikasi; sisa hanya **QA perangkat nyata**.
- Aturan proyek (lihat `CLAUDE.md`): pisahkan `models/ api/ services/ views/`, CSS custom
  **hanya** di `static/css/custom.css`, UI Bahasa Indonesia, Tailwind utility-first,
  Alpine.js (bukan jQuery), Chart.js, Material Symbols (bukan emoji).
- ⚠️ **Drift dokumentasi:** `CLAUDE.md` masih menyebut brand teal/pink + Manrope, padahal
  aplikasi nyata pakai **Indigo `#6366F1` + Amber `#F59E0B`**, **Plus Jakarta Sans + Space
  Grotesk** (lihat `base.html` `tailwind.config`). Perbarui `CLAUDE.md` saat sempat.
- Saat menambah fitur: jaga `requirements.txt` tetap ramping; bila butuh lib berat,
  taruh di `requirements-dev.txt` dan buat fallback yang aman tanpa lib itu (pola yang
  sama seperti `market_service.py` terhadap yfinance).
