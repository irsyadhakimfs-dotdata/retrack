# Template PPT — Project II Data Warehouse
## "ReTrack: Data Warehouse untuk Personal Finance Tracker"

> **Cara pakai file ini:** tiap heading `## Slide N` = satu slide PPT.
> Bagian **Judul/Bullet** = teks yang ditaruh di slide (ringkas, jangan paragraf panjang).
> Bagian **🎤 Narasi** = yang kamu ucapkan saat presentasi (jangan ditulis di slide).
> Bagian **📷 Screenshot** = gambar yang harus kamu siapkan dari aplikasi/DB Browser.
>
> Deadline PPT: **Minggu, 31 Mei 2026 pukul 22.00** · Presentasi: **Rabu, 3 Juni 2026**
> Target jumlah slide: **18–20 slide** (cukup untuk presentasi 10–15 menit).

---

## Slide 1 — Cover

**Judul:**
- ReTrack — Perancangan Data Warehouse untuk Personal Finance Tracker
- Tugas Project Based Data Warehouse Ke-II
- Tahun Ajaran 2025/2026

**Sub:**
- Nama / NIM
- Program Studi Data Science
- Nama Dosen Pengampu

🎤 *Narasi:* "Selamat siang, saya akan mempresentasikan rancangan Data Warehouse dengan topik ReTrack, sebuah aplikasi pencatat keuangan pribadi."

---

## Slide 2 — Agenda / Outline

**Bullet (urut sesuai instruksi tugas):**
1. Latar belakang & topik (ReTrack)
2. Pentingnya Data Warehouse — manfaat & tantangan
3. Arsitektur DWH (Bottom-Up / Kimball)
4. Desain: Conceptual → Logical → Physical
5. Software perancangan DWH
6. Proses ETL (Extract – Transform – Load)
7. Software & hasil visualisasi data (dashboard)
8. Kesimpulan

🎤 *Narasi:* Sebutkan agenda mengikuti 6 poin wajib di lembar tugas + intro & penutup.

---

## Slide 3 — Latar Belakang Topik (ReTrack)

**Bullet:**
- ReTrack = aplikasi web pencatat keuangan & budget planner untuk anak muda Indonesia (18–30 th).
- Sumber data operasional (OLTP): transaksi, dompet (wallet), kategori, budget, savings goal.
- Fitur khas: **deteksi erosi nilai** — seberapa tergerus daya beli pemasukan Rupiah akibat pelemahan kurs USD/IDR.
- Data transaksi terus bertumbuh → butuh analisis multi-periode (bulanan, kuartalan, tahunan).

🎤 *Narasi:* Jelaskan ReTrack sudah punya database operasional, dan kita menambah lapisan DWH di atasnya untuk kebutuhan analitik.

📷 *Screenshot (opsional):* halaman Dashboard / Transaksi aplikasi ReTrack.

---

## Slide 4 — Pentingnya Data Warehouse (Permasalahan)

**Bullet — Mengapa butuh DWH:**
- Database OLTP dioptimalkan untuk **transaksi (insert/update cepat)**, BUKAN untuk agregasi besar.
- Query analitik (total pengeluaran per bulan, tren 12 bulan, top kategori) **memberatkan tabel OLTP** dan memperlambat aplikasi.
- Struktur OLTP ternormalisasi → butuh banyak JOIN untuk laporan → lambat & rumit.
- Tidak ada dimensi waktu yang siap pakai (quarter, nama bulan, weekend) untuk slicing data.

🎤 *Narasi:* Tekankan pemisahan beban: OLTP untuk operasional, DWH untuk analitik.

---

## Slide 5 — Manfaat & Tantangan DWH

**Bullet — Manfaat utama:**
- Query analitik cepat (skema denormalisasi, sedikit JOIN).
- Dimensi waktu siap pakai → analisis tren, musiman, weekend vs weekday.
- Single source of truth untuk pelaporan & dashboard.
- Mendukung pengambilan keputusan keuangan personal berbasis data.

**Bullet — Tantangan implementasi:**
- Menjaga **konsistensi data** OLTP → DWH (proses ETL harus benar).
- **Idempotensi ETL** — menjalankan ETL berulang tidak boleh menduplikasi data.
- Sinkronisasi data eksternal (kurs USD/IDR) yang dipakai menghitung erosi.
- Penyimpanan ganda (data tersalin) & jadwal refresh data.

🎤 *Narasi:* Jujur sebutkan tantangan; tunjukkan solusi idempotensi kita pakai PK = id transaksi.

---

## Slide 6 — Arsitektur DWH yang Digunakan

**Bullet:**
- Pendekatan: **Bottom-Up (Metodologi Kimball)**.
- Mulai dari **satu data mart** paling kritis: data mart **Transaksi Keuangan**.
- Data mart bisa dikembangkan ke fakta lain (budget, goals) bila perlu → membentuk enterprise DWH bertahap.
- DWH disimpan satu basis data dengan OLTP, tabel dipisah dengan prefix `dwh_`.

**Kenapa Bottom-Up (bukan Top-Down/Inmon)?**
- Skala personal finance kecil → tidak perlu enterprise DWH besar di awal.
- Cepat memberi nilai (dashboard langsung jadi), iteratif, biaya rendah.

🎤 *Narasi:* Bandingkan singkat: Top-Down (Inmon) bangun EDW dulu baru data mart; Bottom-Up (Kimball) bangun data mart dulu. Kita pilih Bottom-Up.

📷 *Diagram arsitektur:* OLTP (transactions/users/wallets/categories) → **ETL** → DWH Star Schema → **Chart.js Dashboard**.

---

## Slide 7 — Desain (a) Conceptual Design

**Bullet — 1 Tabel Fakta + 4 Tabel Dimensi:**

**Tabel Fakta — `fact_transaction`** (grain: 1 baris per transaksi)
- Measures: `amount` (SUM/AVG/COUNT), `erosi_persen` (AVG)
- Derived: total_income, total_expense, selisih (net)
- FK: date_id, user_id, wallet_id, category_id

**Tabel Dimensi:**
- `dim_date` — day, month, month_name, quarter, year, day_of_week, is_weekend
- `dim_user` — name, email, created_at
- `dim_wallet` — name, type
- `dim_category` — name, kind (income/expense)

🎤 *Narasi:* Jelaskan grain (level detail) fakta = per transaksi, lalu sebutkan ukuran (measure) dan dimensi pengirisnya.

---

## Slide 8 — Desain (b) Logical Design: STAR SCHEMA

**Diagram (gambar ulang di PPT, rapi):**
```
          dim_date
              |
dim_category — fact_transaction — dim_wallet
              |
          dim_user
```

**Kenapa Star Schema (bukan Snowflake / Galaxy)?**
- Tiap dimensi hanya **1 level hierarki** → tidak perlu dinormalisasi jadi snowflake.
- **Lebih sedikit JOIN** → query agregasi lebih cepat.
- **Mudah dipahami** & dijelaskan (cocok presentasi & skala kecil).
- Belum perlu Galaxy (multi-fakta berbagi dimensi) karena baru 1 tabel fakta.

🎤 *Narasi:* Tunjukkan bentuk bintang: fakta di tengah, dimensi mengelilingi. Tegaskan alasan memilihnya.

📷 *Screenshot:* diagram relasi dari **DB Browser for SQLite** (menu Database Structure) yang menunjukkan tabel `dwh_*`.

🖼️ *Diagram siap pakai:* render salah satu versi di **`dwh/star-schema-mermaid.md`** (ER / bentuk bintang) lewat https://mermaid.live → ekspor PNG → tempel ke slide ini.

---

## Slide 9 — Desain (c) Physical Design — DDL Tabel Dimensi

**Tampilkan potongan SQL (dari `dwh_star_schema.sql`):**
```sql
CREATE TABLE dwh_dim_date (
    date_id     VARCHAR(8) PRIMARY KEY,   -- "20260531"
    full_date   DATE NOT NULL,
    day         INTEGER,
    month       INTEGER,
    month_name  VARCHAR(20),              -- "Mei"
    quarter     INTEGER,
    year        INTEGER,
    day_of_week VARCHAR(10),              -- "Sabtu"
    is_weekend  BOOLEAN
);
```

🎤 *Narasi:* Sebut tipe data dan kunci. Tampilkan juga `dim_category` & `dim_wallet` bila muat.

📷 *Screenshot WAJIB:* eksekusi `CREATE TABLE` di DB Browser + tabel muncul di panel struktur (output).

---

## Slide 10 — Physical Design — DDL Tabel Fakta

**Tampilkan SQL:**
```sql
CREATE TABLE dwh_fact_transaction (
    fact_id          INTEGER PRIMARY KEY,   -- = id transaksi OLTP (idempoten)
    date_id          VARCHAR(8) REFERENCES dwh_dim_date(date_id),
    user_id          INTEGER    REFERENCES dwh_dim_user(user_id),
    wallet_id        INTEGER    REFERENCES dwh_dim_wallet(wallet_id),
    category_id      INTEGER    REFERENCES dwh_dim_category(category_id),
    amount           NUMERIC(15,2),
    kind             VARCHAR(10),           -- income / expense
    usd_rate_at_date FLOAT,
    erosi_persen     FLOAT,
    etl_loaded_at    DATETIME
);
```

🎤 *Narasi:* Tekankan `fact_id` = PK dari id transaksi OLTP → kunci idempotensi ETL. Semua FK menunjuk dimensi (bentuk star).

📷 *Screenshot WAJIB:* hasil eksekusi DDL + daftar tabel `dwh_fact_transaction` di DB.

---

## Slide 11 — Software Perancangan DWH

**Bullet — Tools yang dipakai:**
- **SQLite** — engine basis data DWH (embedded, satu file `.db`).
- **SQLAlchemy ORM + Flask-Migrate (Alembic)** — definisi tabel & migrasi schema.
- **DB Browser for SQLite** — visual desain tabel, jalankan & screenshot query.
- Python 3.11 + Flask sebagai aplikasi induk.

**Keunggulan:**
- Zero-config, gratis, ringan, satu file mudah dibawa & di-backup.
- Terintegrasi langsung dengan aplikasi (DWH satu DB dengan OLTP).

**Keterbatasan:**
- Bukan untuk skala enterprise / concurrent write tinggi.
- Tidak ada fitur OLAP bawaan (partisi, materialized view) seperti DWH besar (BigQuery, Snowflake).
- Tipe data terbatas (mis. boolean & numeric disimpan sederhana).

🎤 *Narasi:* Jujur akui keterbatasan, tapi tepat untuk skala personal finance.

---

## Slide 12 — Proses ETL — Gambaran Umum

**Bullet — alur:**
```
OLTP (transactions, users, wallets, categories)
        │  EXTRACT  (baca data sumber)
        ▼
   TRANSFORM (bangun dim_date, normalisasi dimensi, hitung erosi_persen)
        ▼
     LOAD (db.session.merge → tabel dwh_*, idempoten)
        ▼
   DWH Star Schema  →  return {loaded, skipped, errors}
```

**Bullet:**
- Dijalankan via endpoint `POST /api/dwh/etl/run`.
- ETL **tidak pernah mengubah data OLTP** (read-only terhadap sumber).
- **Idempoten:** dijalankan 2× tidak menambah baris (cek `fact_id` sudah ada → skip).

🎤 *Narasi:* Jelaskan 3 tahap E-T-L singkat lalu masuk detail di slide berikut.

---

## Slide 13 — ETL: EXTRACT

**Bullet:**
- Baca seluruh transaksi milik user dari tabel OLTP `transactions`.
- Baca data referensi: `users`, `wallets`, `categories`.
- Ambil kurs USD/IDR terkini (untuk hitung erosi) — boleh gagal (fallback `None`).

**Tampilkan SQL contoh ekstraksi (dari file SQL):**
```sql
SELECT t.id, t.user_id, t.wallet_id, t.category_id,
       t.amount, t.kind, t.date, t.usd_rate_at_date
FROM transactions t
WHERE t.user_id = :user_id;
```

📷 *Screenshot:* hasil SELECT di atas (beberapa baris transaksi mentah).

---

## Slide 14 — ETL: TRANSFORM

**Bullet — transformasi yang dilakukan:**
- **Generate `dim_date`** dari tiap tanggal unik: `date_id="YYYYMMDD"`, month_name & day_of_week **Bahasa Indonesia**, quarter, is_weekend.
- **Normalisasi dimensi** (upsert user/wallet/category — tanpa duplikat).
- **Hitung `erosi_persen`** memakai rumus daya beli:

```
nilai_usd_awal     = amount / kurs_saat_transaksi
nilai_usd_sekarang = amount / kurs_sekarang
erosi_persen       = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal * 100
```
Contoh: Rp5.000.000, kurs 15.000 → 16.000 ⇒ erosi ≈ **6,25%** daya beli tergerus.

🎤 *Narasi:* Ini nilai tambah analitik kita — fakta diperkaya dengan kolom turunan `erosi_persen`.

📷 *Screenshot:* contoh perhitungan (bisa tabel kecil sebelum→sesudah transform).

---

## Slide 15 — ETL: LOAD

**Bullet:**
- Muat ke tabel `dwh_*` memakai **UPSERT** (`db.session.merge` / `INSERT OR REPLACE`).
- `fact_id` = `transaction.id` → idempoten, tak ada baris ganda.
- Catat waktu muat `etl_loaded_at`.
- Kembalikan statistik: `{"loaded": N, "skipped": M, "errors": 0}`.

**Tampilkan SQL load (dari file SQL):**
```sql
INSERT OR REPLACE INTO dwh_fact_transaction
    (fact_id, date_id, user_id, wallet_id, category_id,
     amount, kind, usd_rate_at_date, erosi_persen, etl_loaded_at)
VALUES (:fact_id, :date_id, :user_id, :wallet_id, :category_id,
        :amount, :kind, :usd_rate, :erosi, CURRENT_TIMESTAMP);
```

📷 *Screenshot WAJIB:* respons JSON endpoint `POST /api/dwh/etl/run` → `{"ok":true,"data":{"loaded":..,"skipped":..,"errors":0}}` (dari browser/Postman).
📷 *Screenshot bukti idempoten:* jalankan ETL 2×, kedua kalinya `loaded:0, skipped:N`.

---

## Slide 16 — Software Visualisasi & Digital Dashboard

**Bullet:**
- **Software visualisasi: Chart.js** (di halaman `/dwh-dashboard` aplikasi ReTrack).
- Data diambil dari endpoint query DWH: `/api/dwh/summary`, `/api/dwh/top-categories`, `/api/dwh/erosi-summary`.

**Yang divisualisasikan + jenis diagram:**
| Visualisasi | Sumber | Diagram |
|---|---|---|
| Pemasukan vs Pengeluaran per bulan | `/api/dwh/summary` | **Bar chart** (grouped) |
| Top 5 kategori pengeluaran | `/api/dwh/top-categories` | **Doughnut / Pie chart** |
| Rata-rata erosi nilai pemasukan | `/api/dwh/erosi-summary` | **KPI Card (angka)** |

🎤 *Narasi:* Contoh kalimat tugas: "Total pengeluaran berdasarkan kategori menggunakan diagram doughnut."

---

## Slide 17 — Query Analitik DWH + Output

**Tampilkan SQL agregasi (dari file SQL), mis. income vs expense per bulan:**
```sql
SELECT d.month, d.month_name, f.kind, SUM(f.amount) AS total
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE d.year = 2026
GROUP BY d.month, d.month_name, f.kind
ORDER BY d.month;
```

📷 *Screenshot WAJIB:* hasil query di DB Browser **DAN** hasil chart di halaman DWH Dashboard.

🎤 *Narasi:* Tunjukkan bahwa query agregasi langsung memberi data untuk chart — inilah nilai DWH.

---

## Slide 18 — Demo Dashboard (Screenshot)

📷 *Screenshot WAJIB (halaman `/dwh-dashboard`):*
- Bar chart pemasukan vs pengeluaran per bulan.
- Doughnut top kategori pengeluaran.
- Card rata-rata erosi nilai + jumlah transaksi income.
- Label "Data Warehouse Mode".

🎤 *Narasi:* Demokan tombol "Jalankan ETL" lalu chart ter-update — tutup dengan menegaskan alur OLTP→ETL→DWH→Dashboard berjalan utuh.

---

## Slide 19 — Kesimpulan

**Bullet:**
- DWH ReTrack memisahkan beban analitik dari operasional → laporan cepat & ringan.
- Desain **Star Schema** (1 fakta + 4 dimensi) tepat untuk skala personal finance.
- Arsitektur **Bottom-Up (Kimball)** memberi data mart yang langsung berguna.
- ETL idempoten + kolom turunan `erosi_persen` = nilai analitik tambahan.
- Visualisasi Chart.js menjadikan data actionable bagi pengguna.

**Pengembangan ke depan:** tambah fakta budget & goals (menuju Galaxy schema), penjadwalan ETL otomatis.

---

## Slide 20 — Penutup / Tanya Jawab

- Terima kasih.
- "Ada pertanyaan?"
- Cantumkan kontak / nama tim.

---

## ✅ Checklist Screenshot Wajib (sesuai tuntutan tugas)

Tugas meminta screenshot query/syntax + output di 3 titik:

- [ ] **Physical design** — `CREATE TABLE` dimensi & fakta + tabel muncul di DB (Slide 9–10)
- [ ] **ETL** — SELECT extract, perhitungan transform, INSERT/UPSERT load + respons JSON `etl/run` (Slide 13–15)
- [ ] **Visualisasi** — query agregasi + chart di dashboard (Slide 17–18)

> File SQL ilustrasi lengkap: **`dwh/dwh_star_schema.sql`** — buka di DB Browser for SQLite untuk eksekusi & screenshot.
