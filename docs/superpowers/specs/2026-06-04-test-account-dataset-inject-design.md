# Spec — Dataset realistis "Andi" + inject sebagai akun test ke Vercel prod

> Tanggal: 2026-06-04 · Status: disetujui untuk lanjut ke implementation plan

## 1. Tujuan

Mengubah dataset `injectable/andi_karyawan_hemat_beli_bensin.csv` menjadi lebih
realistis: transaksi membentang **Januari 2025 hingga hari ini (2026-06-04)**,
dengan **lebih banyak kategori dan rekening/dompet**, lalu **menyuntikkan** data
itu ke database produksi (Vercel/Neon Postgres) sebagai **akun test baru**.

Deliverable akhir ke user: **email, nama, password** akun test.

## 2. Konteks teknis (temuan)

- **DB produksi = Neon Postgres** (`ProdConfig` membaca `DATABASE_URL`).
  `.env` lokal hanya `FLASK_ENV=development` → lokal pakai SQLite. URL Neon TIDAK
  tersedia lokal sampai ditarik via Vercel CLI.
- **`scripts/import_keuangan_csv.py` sudah ada.** Perilaku: cari user by email →
  **hapus semua transaksi lama user itu** (+ fakta DWH) → baca CSV → cocokkan
  `Kategori`/`Dompet` **ke baris yang HARUS sudah ada** (match by name,
  case-insensitive); baris yang tak cocok dilewati.
- **Registrasi TIDAK auto-seed** kategori/dompet. Maka kategori + dompet harus
  dibuat lebih dulu sebelum import, atau semua baris transaksi akan dilewati.
- Kolom DB: `Wallet.type ∈ {cash, bank, ewallet}`, `Wallet.initial_balance`;
  `Category.kind ∈ {income, expense}`; `Transaction(user_id, wallet_id,
  category_id, amount, kind, date(datetime), note, usd_rate_at_date)`.
- `psycopg2-binary` ada di `requirements.txt` (driver Postgres). Akan diverifikasi
  terpasang di venv lokal sebelum konek ke Neon.
- Prod menjalankan `db.create_all()` saat cold start → skema Neon sudah ada;
  seed hanya meng-INSERT baris.

## 3. Keputusan (disetujui)

| Aspek | Keputusan |
|---|---|
| Metode inject | **Vercel CLI → `vercel env pull`** (aman, tanpa paste kredensial) |
| Skup dataset | **Kaya tapi konsisten persona** (Andi hemat, ~12–15 kategori, ~5 dompet) |
| Identitas akun | email `test@retrack.app`, nama `Test Data`, password `12345678` |
| File CSV | **Overwrite** file bernama sama; backup asli ke `…_beli_bensin.orig.csv` |
| Kenaikan gaji | Naik ke **BSI 3.0jt + Gopay 750k mulai September 2025** |

## 4. Komponen / file

| File | Status | Tujuan |
|---|---|---|
| `scripts/generate_andi_dataset.py` | baru | Generator deterministik (seed tetap) → tulis CSV kaya. Re-runnable. |
| `injectable/andi_karyawan_hemat_beli_bensin.csv` | ditimpa | Versi kaya. Asli → `…_beli_bensin.orig.csv`. |
| `scripts/seed_test_account.py` | baru | Idempoten: buat/temukan user `test@retrack.app`, buat dompet + kategori (nama persis seperti di CSV), set initial_balance. |
| `scripts/import_keuangan_csv.py` | dipakai ulang apa adanya | Import CSV ke user. |

Pemisahan layer dijaga: generator = util data murni (tak sentuh DB); seed = util
DB idempoten; import = skrip yang sudah ada. Tak ada perubahan di `app/`.

## 5. Part A — Desain dataset

Persona: **Andi**, pekerja muda hemat, komuter motor, gaji ~Rp3,5jt/bln.

- **Rentang:** 2025-01-01 → 2026-06-04. Target ~1,3 trx/hari ≈ **~680 baris**.
- **5 dompet** (`type`, `initial_balance`):
  - `Cash` (cash, 150.000)
  - `BSI` (bank, 500.000) — rekening gaji utama
  - `Gopay` (ewallet, 50.000)
  - `Dana` (ewallet, 100.000)
  - `Bank Jago` (bank, 300.000) — kantong tabungan
- **15 kategori:**
  - income: `Gaji`, `THR/Bonus`, `Cashback`
  - expense: `Makanan`, `Bensin`, `Kos`, `Listrik & Air`, `Internet & Pulsa`,
    `Transportasi`, `Belanja`, `Kesehatan`, `Hiburan`, `Kopi & Jajan`,
    `Transfer Keluarga`, `Nabung`

### Model arus kas (per bulan)

- **Gaji** akhir bulan: sebelum Sep 2025 → BSI 2.800.000 + Gopay 700.000;
  mulai Sep 2025 → BSI 3.000.000 + Gopay 750.000.
- **THR/Bonus** dekat Lebaran: ~akhir Maret 2025 dan ~pertengahan Maret 2026,
  ≈ 1× gaji (sebagian ke BSI, sebagian ke Bank Jago agar tabungan tumbuh).
- **Cashback** kecil sesekali (Gopay/Dana), 2.000–15.000.
- **Pengeluaran rutin bulanan:** `Kos` (~600–700k), `Listrik & Air` (~80–120k),
  `Internet & Pulsa` (~80–120k).
- **Pengeluaran sering kecil:** `Makanan` (12k–25k, hampir tiap hari),
  `Bensin` (10k–20k, ~2–3×/minggu), `Kopi & Jajan` (8k–25k).
- **Sesekali:** `Transportasi` (parkir/servis), `Belanja` (kebutuhan/toiletries),
  `Kesehatan`, `Hiburan`, `Transfer Keluarga` (~200–400k), `Nabung` (~200–400k).
- **Net per bulan sedikit positif** (hemat → nabung).

### Kurs USD (kolom "Kurs USD saat transaksi", hanya baris income)

Tabel kurs per bulan, tren naik & **berakhir di 17.673 pada Apr–Jun 2026** agar
nyambung dengan data lama:

| Bulan | Kurs | Bulan | Kurs |
|---|---|---|---|
| 2025-01 | 16.200 | 2025-10 | 16.800 |
| 2025-02 | 16.300 | 2025-11 | 17.000 |
| 2025-03 | 16.500 | 2025-12 | 17.200 |
| 2025-04 | 16.400 | 2026-01 | 17.400 |
| 2025-05 | 16.300 | 2026-02 | 17.500 |
| 2025-06 | 16.250 | 2026-03 | 17.600 |
| 2025-07 | 16.200 | 2026-04 | 17.673 |
| 2025-08 | 16.400 | 2026-05 | 17.673 |
| 2025-09 | 16.600 | 2026-06 | 17.673 |

### Format CSV (header dipertahankan)

```
"Tanggal","Jenis","Kategori","Dompet","Nominal (Rp)","Catatan","Kurs USD saat transaksi"
```
- `Jenis` ∈ {`Pemasukan`, `Pengeluaran`} (sesuai `PETA_JENIS` di import script).
- `Tanggal` = `YYYY-MM-DD`. Kurs hanya diisi untuk income; expense kosong `""`.
- Catatan natural Bahasa Indonesia (mis. "nasi warteg", "isi bensin", "bayar kos").

### Determinisme & jaminan

- Generator memakai `random.Random(seed_tetap)` → output dapat direproduksi.
- Sebelum menulis, generator **mensimulasikan saldo tiap dompet** sepanjang
  periode dan **assert tiap dompet ≥ 0** setiap saat. Jika ada yang negatif,
  generator gagal (exit non-zero) — bukan menulis data cacat.

## 6. Part B — Workflow inject ke Vercel/Neon

1. Pastikan Node/npm ada → `npm i -g vercel`. (Jika user belum login) user jalankan
   `! vercel login` di sesi.
2. `vercel link` ke proyek ini (pilih proyek ReTrack yang sudah ada di Vercel).
3. `vercel env pull .env.production` → berisi `DATABASE_URL` Neon.
   `.env.production` TIDAK di-commit (cek `.gitignore`; tambah bila perlu).
4. Jalankan dengan env produksi:
   ```
   FLASK_ENV=production DATABASE_URL=<neon> python scripts/seed_test_account.py
   FLASK_ENV=production DATABASE_URL=<neon> python scripts/import_keuangan_csv.py \
       "injectable/andi_karyawan_hemat_beli_bensin.csv" test@retrack.app
   ```
   (Di PowerShell pakai `$env:FLASK_ENV=...; $env:DATABASE_URL=...` lalu jalankan.)
5. **Keamanan:** email target di-hardcode `test@retrack.app` di `seed_test_account.py`;
   import dipanggil dengan email yang sama. **Tidak pernah** menyentuh
   `irsyadhakimfs@gmail.com`. Kedua skrip idempoten/aman diulang.

## 7. Verifikasi (urutan wajib)

1. **Dry-run lokal (SQLite dev) dulu:** jalankan seed + import tanpa
   `DATABASE_URL` (default dev). Cek:
   - jumlah baris diimpor ≈ jumlah baris CSV (0 baris "dilewati"),
   - `seed` membuat 5 dompet + 15 kategori,
   - saldo tiap dompet non-negatif.
2. **Baru ke prod** setelah dry-run bersih.
3. **Setelah inject prod:** verifikasi via API live —
   `POST /api/auth/login` dengan `test@retrack.app` / `12345678` →
   `GET /api/transactions` mengembalikan data (jumlah masuk akal).

## 8. Deliverable ke user

```
Email    : test@retrack.app
Nama     : Test Data
Password : 12345678
```
plus ringkasan satu baris: jumlah transaksi, rentang tanggal, jumlah
kategori & dompet yang dibuat.

## 9. Di luar skup (YAGNI)

- Tidak menambah fitur transfer antar-dompet (tak didukung model).
- Tidak mengubah kode `app/` (model/api/views/services).
- Tidak menyentuh CSV lain di `injectable/`.
- Tidak membuat goal/budget/gold untuk akun test (boleh menyusul bila diminta).
