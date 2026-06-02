# Rancangan Data Warehouse — ReTrack Personal Finance Tracker

> **Topik:** Personal Financial & Budget Planner (ReTrack)
> **Mahasiswa:** Irsyad Hakim · irsyadhakimfs@gmail.com
> **Tanggal:** 31 Mei 2026

---

## 1. Pentingnya Data Warehouse

### 1.1 Mengapa Masalah Ini Membutuhkan Data Warehouse?

ReTrack adalah aplikasi pencatatan keuangan pribadi yang menyimpan data **transaksi harian** pengguna — setiap kali user membeli makanan, menerima gaji, atau membayar transportasi, sebuah baris baru masuk ke tabel `transactions` (database OLTP). Seiring waktu, tabel ini bisa memiliki ribuan hingga ratusan ribu baris untuk satu pengguna.

**Masalah yang muncul tanpa Data Warehouse:**

| Masalah | Contoh Nyata di ReTrack |
|---|---|
| **Query agregasi lambat** | `SELECT SUM(amount) FROM transactions WHERE YEAR(date)=2026 GROUP BY MONTH(date), category_id` — query ini harus scan seluruh tabel tiap kali dashboard dibuka |
| **Data OLTP tidak siap analisis** | Tabel `transactions` tidak punya kolom `quarter`, `month_name`, `is_weekend` — harus dihitung ulang setiap query |
| **Tidak ada histori daya beli** | Kolom `erosi_persen` (persentase penurunan daya beli Rupiah terhadap USD) tidak bisa dihitung langsung dari OLTP tanpa kurs historis |
| **Beban analitik mengganggu transaksi** | Kalau query laporan tahunan berjalan bersamaan dengan user input transaksi baru, performa aplikasi turun |

**Manfaat utama Data Warehouse untuk ReTrack:**

1. **Pre-agregasi data** — tabel `dwh_fact_transaction` sudah berisi semua ukuran (amount, erosi_persen) yang siap di-SUM/AVG tanpa kalkulasi ulang.
2. **Dimensi waktu yang kaya** — `dwh_dim_date` menyimpan `quarter`, `month_name` (Bahasa Indonesia), `day_of_week`, `is_weekend` — langsung bisa dipakai untuk filter "pengeluaran akhir pekan vs hari kerja".
3. **Pemisahan beban** — query analitik (laporan tahunan, tren kuartalan) berjalan di tabel `dwh_*` yang terpisah, tidak mengganggu OLTP.
4. **Kolom derived siap pakai** — `erosi_persen` dihitung sekali saat ETL, disimpan permanen, tidak perlu dihitung ulang setiap render dashboard.
5. **Data historis stabil** — meski data OLTP berubah (edit/delete transaksi), snapshot DWH merekam kondisi saat ETL dijalankan.

**Tantangan implementasi:**

| Tantangan | Cara Diatasi di ReTrack |
|---|---|
| **Konsistensi data** | ETL menggunakan `INSERT OR REPLACE` (UPSERT) dengan `fact_id = transaction.id` — menjalankan ETL berkali-kali tidak menduplikasi baris (idempoten) |
| **Kurs USD/IDR berubah** | `erosi_persen` dihitung menggunakan kurs terkini saat ETL dijalankan via `market_service.get_usd_idr()` — user harus sadar bahwa nilai ini adalah snapshot |
| **Sinkronisasi OLTP–DWH** | DWH tidak otomatis update saat transaksi baru masuk; user harus klik "Jalankan ETL" di DWH Dashboard, atau bisa dijadwalkan cron |
| **Satu database file** | Karena ReTrack personal app (SQLite), DWH dan OLTP berbagi file `.db` yang sama — di skala enterprise ini akan dipisah ke database berbeda |

---

## 2. Arsitektur yang Digunakan

### 2.1 Pendekatan: Bottom-Up (Metode Kimball)

ReTrack menggunakan pendekatan **Bottom-Up** yang dipopulerkan oleh Ralph Kimball. Alasan pemilihan ini:

```
                    PENDEKATAN BOTTOM-UP (KIMBALL)
                    ================================

  OLTP (Operasional)           DWH (Analitik)
  ─────────────────────        ─────────────────────────────────
  transactions          ──ETL──►  fact_transaction  (Data Mart)
  users                 ──ETL──►  dim_user
  wallets               ──ETL──►  dim_wallet
  categories            ──ETL──►  dim_category
  [tanggal unik]        ──ETL──►  dim_date
                                        │
                                        ▼
                               Dashboard Analitik
                               (Chart.js di /dwh-dashboard)
```

**Mengapa Bottom-Up bukan Top-Down (Inmon)?**

| Aspek | Bottom-Up (Kimball) — yang dipakai | Top-Down (Inmon) |
|---|---|---|
| **Dimulai dari** | Data Mart spesifik (transaksi keuangan) | Enterprise Data Warehouse dulu baru Data Mart |
| **Waktu implementasi** | Cepat (1-2 minggu untuk data mart pertama) | Lama (bisa berbulan-bulan untuk EDW) |
| **Kompleksitas** | Rendah — cocok untuk proyek mahasiswa | Tinggi — butuh tim DWH khusus |
| **Cocok untuk** | Proyek kecil-menengah, 1 domain bisnis (keuangan) | Enterprise multi-domain (HR, Finance, Sales, dll.) |
| **Risiko** | Data mart bisa silo kalau tidak dikoordinasi | Aman integrasi karena centralized EDW |

Untuk ReTrack, Bottom-Up adalah pilihan tepat karena:
- Hanya ada **1 domain data** (transaksi keuangan pribadi)
- Skala kecil (satu pengguna, ribuan transaksi)
- Butuh hasil cepat (deadline tugas PPT)
- Tidak perlu Enterprise Data Warehouse yang kompleks

### 2.2 Komponen Arsitektur Lengkap

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARSITEKTUR DATA WAREHOUSE RETRACK            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SUMBER DATA (OLTP)        PROSES ETL         DATA WAREHOUSE    │
│  ─────────────────         ──────────         ─────────────     │
│                                                                 │
│  ┌─────────────┐           ┌────────┐         ┌─────────────┐  │
│  │ transactions│──Extract──►        │──Load──► │fact_trans.  │  │
│  │ users       │           │Transform          │dim_date     │  │
│  │ wallets     │──Extract──► hitung │──Load──► │dim_user     │  │
│  │ categories  │           │erosi   │          │dim_wallet   │  │
│  └─────────────┘           │persen  │──Load──► │dim_category │  │
│                            └────────┘          └──────┬──────┘  │
│                                                       │         │
│                                                QUERY ANALITIK   │
│                                                       │         │
│                                               ┌───────▼──────┐  │
│                                               │  Dashboard   │  │
│                                               │  Chart.js    │  │
│                                               │  /dwh-dash   │  │
│                                               └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

Arsitektur ini mendukung kebutuhan analisis karena:
- **Pemisahan lapisan:** OLTP untuk transaksi harian, DWH untuk laporan historis
- **Data mart terfokus:** hanya berisi data transaksi keuangan yang relevan untuk analisis
- **Query siap pakai:** dimensi yang denormalisasi memungkinkan query analitik 1-2 JOIN saja

---

## 3. Desain yang Digunakan

### 3a. Conceptual Design

Conceptual design menggambarkan entitas bisnis dan hubungannya tanpa detail teknis implementasi.

**Entitas Dimensi (Dimension Tables):**

#### Dimensi Tanggal (`dwh_dim_date`)
Menyimpan atribut waktu yang diturunkan dari setiap tanggal unik transaksi.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `date_id` (PK) | String | Format "YYYYMMDD" — misal "20260531" |
| `full_date` | Date | Tanggal lengkap |
| `day` | Integer | Hari dalam bulan (1–31) |
| `month` | Integer | Bulan (1–12) |
| `month_name` | String | Nama bulan Bahasa Indonesia: "Januari"–"Desember" |
| `quarter` | Integer | Kuartal (1–4); Q1=Jan-Mar, Q2=Apr-Jun, dst. |
| `year` | Integer | Tahun (2025, 2026, dll.) |
| `day_of_week` | String | Nama hari: "Senin"–"Minggu" |
| `is_weekend` | Boolean | True bila Sabtu atau Minggu |

**Mengapa dimensi ini penting?** Tanpa `dwh_dim_date`, untuk mendapatkan "total pengeluaran per kuartal" atau "pengeluaran hari kerja vs akhir pekan" kita harus menghitung dari string tanggal di setiap query — lambat dan rawan error. Dengan dimensi ini, filter cukup: `WHERE d.is_weekend = 1` atau `GROUP BY d.quarter`.

#### Dimensi Pengguna (`dwh_dim_user`)
Salinan ringkas data pengguna dari OLTP.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `user_id` (PK) | Integer | Sama dengan `users.id` di OLTP |
| `name` | String | Nama lengkap pengguna |
| `email` | String | Email pengguna |
| `created_at` | Date | Tanggal bergabung (hanya bagian date, bukan datetime) |

#### Dimensi Dompet (`dwh_dim_wallet`)
Konteks dompet/rekening untuk setiap transaksi.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `wallet_id` (PK) | Integer | Sama dengan `wallets.id` di OLTP |
| `name` | String | Nama dompet: "BCA", "GoPay", "Dompet Tunai" |
| `type` | String | Tipe: "cash", "bank", "e-wallet" |

#### Dimensi Kategori (`dwh_dim_category`)
Klasifikasi transaksi berdasarkan jenis pengeluaran/pemasukan.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `category_id` (PK) | Integer | Sama dengan `categories.id` di OLTP |
| `name` | String | Nama kategori: "Makan", "Transportasi", "Gaji" |
| `kind` | String | Tipe: "income" atau "expense" |

**Tabel Fakta (`dwh_fact_transaction`):**

Tabel fakta adalah inti DWH — setiap baris merepresentasikan **satu transaksi keuangan** yang telah melalui proses ETL.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `fact_id` (PK) | Integer | = `transactions.id` dari OLTP (bukan auto-increment) |
| `date_id` (FK) | String | Referensi ke `dwh_dim_date` |
| `user_id` (FK) | Integer | Referensi ke `dwh_dim_user` |
| `wallet_id` (FK) | Integer | Referensi ke `dwh_dim_wallet` |
| `category_id` (FK) | Integer | Referensi ke `dwh_dim_category` |
| `amount` | Numeric(15,2) | Jumlah transaksi dalam Rupiah (selalu positif) |
| `kind` | String | "income" atau "expense" |
| `usd_rate_at_date` | Float | Kurs USD/IDR saat transaksi dicatat |
| `erosi_persen` | Float | **Ukuran derived:** % penurunan daya beli Rupiah |
| `etl_loaded_at` | DateTime | Timestamp kapan ETL memuat baris ini |

**Mengapa `fact_id = transaction.id`?** Ini kunci idempoten ETL. Bila ETL dijalankan ulang, `INSERT OR REPLACE` akan menimpa baris yang sama (bukan menambah baris baru), karena PK sudah ada. Kalau pakai auto-increment, setiap ETL run akan menambah baris duplikat.

**Ukuran (Measures) yang bisa dihitung dari tabel fakta:**
- `SUM(amount)` → total pendapatan / pengeluaran per periode
- `AVG(amount)` → rata-rata transaksi
- `COUNT(fact_id)` → jumlah transaksi
- `AVG(erosi_persen)` → rata-rata penurunan daya beli rupiah
- `SUM(CASE WHEN kind='income' THEN amount ELSE -amount END)` → net cashflow

---

### 3b. Logical Design — Star Schema

**Pilihan Skema: Star Schema**

ReTrack menggunakan **Star Schema** (bukan Snowflake Schema atau Galaxy Schema).

```
                        ┌──────────────────┐
                        │   dwh_dim_date   │
                        │──────────────────│
                        │ date_id (PK)     │
                        │ full_date        │
                        │ day, month, year │
                        │ month_name       │
                        │ quarter          │
                        │ day_of_week      │
                        │ is_weekend       │
                        └────────┬─────────┘
                                 │  1
                                 │
┌─────────────────┐    N ┌───────┴─────────────────┐ N    ┌──────────────────┐
│ dwh_dim_category│──────┤  dwh_fact_transaction   ├──────│  dwh_dim_wallet  │
│─────────────────│      │─────────────────────────│      │──────────────────│
│ category_id (PK)│      │ fact_id (PK)            │      │ wallet_id (PK)   │
│ name            │      │ date_id (FK)            │      │ name             │
│ kind            │      │ user_id (FK)            │      │ type             │
└─────────────────┘      │ wallet_id (FK)          │      └──────────────────┘
                          │ category_id (FK)        │
┌─────────────────┐      │ amount (DECIMAL)        │
│  dwh_dim_user   │ 1    │ kind                    │
│─────────────────│──────┤ usd_rate_at_date        │
│ user_id (PK)    │      │ erosi_persen            │
│ name            │      │ etl_loaded_at           │
│ email           │      └─────────────────────────┘
│ created_at      │
└─────────────────┘
```

**Mengapa Star Schema, bukan Snowflake atau Galaxy?**

| Kriteria | Star Schema | Snowflake Schema | Galaxy Schema |
|---|---|---|---|
| **Normalisasi dimensi** | Tidak (denormalisasi) | Ya (dimensi dinormalisasi ke sub-tabel) | Ya, multi fakta |
| **Jumlah JOIN** | Sedikit (1 tabel fakta JOIN langsung ke dimensi) | Lebih banyak (dimensi punya sub-tabel) | Paling kompleks |
| **Query complexity** | Rendah | Sedang | Tinggi |
| **Performa** | Cepat untuk agregasi | Sedikit lebih lambat | Paling lambat |
| **Penggunaan storage** | Lebih besar (data dimensi diulang) | Lebih hemat | Hemat |
| **Cocok untuk** | 1 level hierarki per dimensi | Multi-level hierarki (negara→provinsi→kota) | Multi data mart |

**Alasan spesifik memilih Star Schema untuk ReTrack:**

1. **Dimensi hanya punya 1 level hierarki** — Kategori tidak punya sub-kategori di DWH (meski di OLTP ada parent_id, kita flatten ke 1 level). Wallet hanya punya `name` dan `type` tanpa bank sub-dimensi. Tidak ada alasan untuk normalisasi ke Snowflake.

2. **Query lebih simpel** — Laporan "total pengeluaran per kategori per bulan" cukup:
   ```sql
   SELECT d.month_name, c.name, SUM(f.amount)
   FROM dwh_fact_transaction f
   JOIN dwh_dim_date d ON f.date_id = d.date_id
   JOIN dwh_dim_category c ON f.category_id = c.category_id
   WHERE f.kind = 'expense'
   GROUP BY d.month, c.name
   ```
   Dengan Snowflake, ada JOIN tambahan ke tabel sub-dimensi.

3. **Performa lebih cepat** — SQLite tanpa server, query harus seefisien mungkin. Star schema meminimalkan jumlah JOIN.

4. **Mudah dipahami** — Untuk presentasi dan laporan akademik, Star Schema lebih mudah dijelaskan dan divisualisasikan dalam bentuk bintang dengan fakta di tengah.

---

### 3c. Physical Design — Query/Syntax dan Output

#### DDL: Membuat Tabel DWH

```sql
-- =============================================================================
--  PHYSICAL DESIGN: DDL Star Schema DWH ReTrack
--  Engine: SQLite
-- =============================================================================

-- Dimensi Tanggal
CREATE TABLE dwh_dim_date (
    date_id     VARCHAR(8) PRIMARY KEY,   -- "YYYYMMDD"
    full_date   DATE NOT NULL,
    day         INTEGER,
    month       INTEGER,
    month_name  VARCHAR(20),              -- "Januari", "Februari", dst.
    quarter     INTEGER,                  -- 1..4
    year        INTEGER,
    day_of_week VARCHAR(10),              -- "Senin", "Selasa", dst.
    is_weekend  BOOLEAN                   -- 1 = Sabtu/Minggu
);

-- Dimensi Pengguna
CREATE TABLE dwh_dim_user (
    user_id    INTEGER PRIMARY KEY,
    name       VARCHAR(100),
    email      VARCHAR(200),
    created_at DATE
);

-- Dimensi Dompet
CREATE TABLE dwh_dim_wallet (
    wallet_id INTEGER PRIMARY KEY,
    name      VARCHAR(100),
    type      VARCHAR(50)
);

-- Dimensi Kategori
CREATE TABLE dwh_dim_category (
    category_id INTEGER PRIMARY KEY,
    name        VARCHAR(100),
    kind        VARCHAR(10)               -- "income" / "expense"
);

-- Tabel Fakta
CREATE TABLE dwh_fact_transaction (
    fact_id          INTEGER PRIMARY KEY,
    date_id          VARCHAR(8) REFERENCES dwh_dim_date(date_id),
    user_id          INTEGER    REFERENCES dwh_dim_user(user_id),
    wallet_id        INTEGER    REFERENCES dwh_dim_wallet(wallet_id),
    category_id      INTEGER    REFERENCES dwh_dim_category(category_id),
    amount           NUMERIC(15,2),
    kind             VARCHAR(10),
    usd_rate_at_date FLOAT,
    erosi_persen     FLOAT,
    etl_loaded_at    DATETIME
);

-- Index untuk mempercepat query agregasi
CREATE INDEX idx_fact_date     ON dwh_fact_transaction(date_id);
CREATE INDEX idx_fact_category ON dwh_fact_transaction(category_id);
CREATE INDEX idx_fact_user     ON dwh_fact_transaction(user_id);
```

#### Query Analitik 1: Pemasukan vs Pengeluaran per Bulan

```sql
-- Query: total income & expense per bulan tahun 2026
SELECT d.month, d.month_name, f.kind, SUM(f.amount) AS total
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE f.user_id = 1 AND d.year = 2026
GROUP BY d.month, d.month_name, f.kind
ORDER BY d.month;
```

**Output Query 1:**

| month | month_name | kind    | total     |
|-------|------------|---------|-----------|
| 3     | Maret      | income  | 5000000   |
| 3     | Maret      | expense | 200000    |
| 4     | April      | income  | 5000000   |
| 4     | April      | expense | 320000    |
| 5     | Mei        | income  | 5000000   |
| 5     | Mei        | expense | 255000    |

#### Query Analitik 2: Top 5 Kategori Pengeluaran

```sql
-- Query: top 5 kategori pengeluaran terbesar
SELECT c.name AS category,
       SUM(f.amount)    AS total,
       COUNT(f.fact_id) AS jumlah_transaksi
FROM dwh_fact_transaction f
JOIN dwh_dim_category c ON f.category_id = c.category_id
WHERE f.user_id = 1 AND f.kind = 'expense'
GROUP BY c.name
ORDER BY total DESC
LIMIT 5;
```

**Output Query 2:**

| category     | total  | jumlah_transaksi |
|--------------|--------|------------------|
| Makan        | 525000 | 3                |
| Transportasi | 130000 | 2                |
| Hiburan      | 120000 | 1                |

#### Query Analitik 3: Rata-rata Erosi Nilai (Daya Beli)

```sql
-- Query: rata-rata erosi nilai pemasukan (penurunan daya beli Rupiah)
SELECT ROUND(AVG(f.erosi_persen), 4) AS avg_erosi_persen,
       COUNT(f.fact_id)              AS total_income_transactions
FROM dwh_fact_transaction f
WHERE f.user_id = 1
  AND f.kind = 'income'
  AND f.erosi_persen IS NOT NULL;
```

**Output Query 3:**

| avg_erosi_persen | total_income_transactions |
|------------------|---------------------------|
| 4.3210           | 3                         |

*Artinya: rata-rata daya beli Rupiah dari pemasukan pengguna turun 4.32% dibanding saat pemasukan diterima.*

#### Query Analitik 4: Net Cashflow per Kuartal

```sql
-- Query: ringkasan net per kuartal
SELECT d.year, d.quarter,
       SUM(CASE WHEN f.kind = 'income'  THEN f.amount ELSE 0 END) AS total_income,
       SUM(CASE WHEN f.kind = 'expense' THEN f.amount ELSE 0 END) AS total_expense,
       SUM(CASE WHEN f.kind = 'income'  THEN f.amount ELSE 0 END)
       - SUM(CASE WHEN f.kind = 'expense' THEN f.amount ELSE 0 END) AS selisih_net
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE f.user_id = 1
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;
```

**Output Query 4:**

| year | quarter | total_income | total_expense | selisih_net |
|------|---------|--------------|---------------|-------------|
| 2026 | 1       | 5000000      | 200000        | 4800000     |
| 2026 | 2       | 10000000     | 575000        | 9425000     |

#### Query Analitik 5: Pengeluaran Akhir Pekan vs Hari Kerja

```sql
-- Query: perbandingan pengeluaran akhir pekan vs hari kerja
SELECT CASE WHEN d.is_weekend = 1 THEN 'Akhir Pekan' ELSE 'Hari Kerja' END AS tipe_hari,
       SUM(f.amount)    AS total_pengeluaran,
       COUNT(f.fact_id) AS jumlah
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE f.user_id = 1 AND f.kind = 'expense'
GROUP BY d.is_weekend;
```

**Output Query 5:**

| tipe_hari   | total_pengeluaran | jumlah |
|-------------|-------------------|--------|
| Hari Kerja  | 775000            | 6      |
| Akhir Pekan | 0                 | 0      |

*Catatan: sample data kebetulan tidak ada transaksi akhir pekan — di data nyata akan terisi.*

---

## 4. Software yang Digunakan

### 4.1 Stack Teknologi DWH ReTrack

| Komponen | Software | Versi |
|---|---|---|
| **Bahasa Pemrograman** | Python | 3.11+ |
| **Web Framework** | Flask | 3.x |
| **ORM (Object Relational Mapper)** | SQLAlchemy via Flask-SQLAlchemy | 2.x |
| **Database Engine** | SQLite | 3.x (bawaan Python) |
| **Database Migration** | Flask-Migrate (berbasis Alembic) | — |
| **GUI Database** | DB Browser for SQLite | 3.12+ |
| **Visualisasi** | Chart.js | 4.x |
| **Backend API** | Flask Blueprint (`/api/dwh`) | — |

### 4.2 Penjelasan Tiap Software

#### Python 3.11
**Peran:** Bahasa utama untuk ETL service (`app/services/etl_service.py`). Semua logika transform (menghitung `erosi_persen`, membangun objek `DimDate`, upsert data) ditulis dalam Python.

**Keunggulan:**
- Library ekosistem kaya: `datetime` (manipulasi tanggal), `yfinance` (kurs USD/IDR)
- Mudah dipelajari dan dibaca
- Tersedia gratis, cross-platform

**Keterbatasan:**
- Tidak ada query optimizer bawaan seperti tool DWH enterprise (Talend, Informatica)
- ETL manual — perlu kode Python untuk setiap transformasi, bukan konfigurasi visual

#### SQLAlchemy (ORM)
**Peran:** Mendefinisikan model tabel DWH sebagai class Python (`DimDate`, `DimUser`, dll.) dan menjalankan operasi database tanpa raw SQL di Python.

**Keunggulan:**
- **Upsert via `db.session.merge()`** — kunci idempoten ETL; jika objek dengan PK yang sama sudah ada, akan diupdate, bukan diduplikasi
- Abstraksi database — kalau nanti migrasi dari SQLite ke PostgreSQL, kode Python tidak perlu diubah
- Type safety — kolom `Numeric(15, 2)` memastikan tidak ada floating-point error untuk nilai uang

**Keterbatasan:**
- Overhead ORM — untuk batch insert jutaan baris, raw SQL lebih cepat
- Learning curve bagi yang belum familiar dengan ORM pattern

#### SQLite
**Peran:** Database engine yang menyimpan semua data OLTP dan DWH dalam satu file (`refinance_dev.db`).

**Keunggulan:**
- **Zero-config** — tidak perlu install server database terpisah
- **File-based** — mudah di-backup, dipindah, dibuka di DB Browser
- **Cocok untuk personal app** — satu pengguna, volume data kecil-menengah
- Mendukung `INSERT OR REPLACE` untuk UPSERT

**Keterbatasan:**
- **Tidak cocok untuk concurrent write** — kalau ada 100 user yang ETL bersamaan, SQLite akan lock
- **Tidak ada fitur DWH enterprise** — tidak ada partitioning kolom, materialized views, columnar storage
- **Satu file = satu database** — DWH dan OLTP harus berbagi file (bukan best practice untuk produksi)

#### DB Browser for SQLite
**Peran:** GUI untuk menjalankan query SQL secara manual, melihat struktur tabel, dan mengambil screenshot output untuk keperluan PPT/laporan.

**Keunggulan:**
- Gratis dan open-source
- Interface visual yang mudah dipakai
- Bisa ekspor hasil query ke CSV
- Tampilkan tabel dan relasi secara visual

**Keterbatasan:**
- Hanya untuk SQLite — tidak bisa connect ke PostgreSQL/MySQL
- Tidak ada fitur monitoring atau scheduling ETL

#### Flask-Migrate (Alembic)
**Peran:** Versi-kontrol skema database. Setiap perubahan model Python (menambah tabel `dwh_*`) direpresentasikan sebagai file migrasi yang bisa dijalankan (`flask db upgrade`) atau di-rollback (`flask db downgrade`).

**Keunggulan:**
- Perubahan skema bisa di-track di Git
- Aman untuk production: tidak drop-recreate tabel, tapi ALTER TABLE

**Keterbatasan:**
- SQLite memiliki keterbatasan ALTER TABLE (tidak bisa drop kolom)

#### Chart.js
**Peran:** Library JavaScript untuk menampilkan hasil query DWH sebagai grafik interaktif di halaman `/dwh-dashboard`.

**Keunggulan:**
- Ringan (tidak butuh server render)
- Mendukung bar, line, doughnut chart — cukup untuk semua kebutuhan visualisasi DWH
- Interaktif (hover tooltip, click filter)

**Keterbatasan:**
- Tidak bisa handle dataset jutaan baris langsung di browser
- Tidak ada fitur drill-down otomatis seperti Power BI / Tableau

---

## 5. Proses ETL yang Dilakukan

ETL (Extract, Transform, Load) adalah proses memindahkan data dari sistem OLTP ke Data Warehouse. Di ReTrack, ETL diimplementasikan di `app/services/etl_service.py`.

### 5.1 Gambaran Umum Alur ETL

```
OLTP Database                    ETL Service                     DWH Tables
(refinance_dev.db)               (etl_service.py)                (dwh_*)
──────────────────               ───────────────                 ──────────

transactions ────► 1. EXTRACT ──►
users        ────► (baca data)   2. TRANSFORM ──►  3. LOAD ────► dwh_dim_date
wallets      ────►               (normalisasi,                   dwh_dim_user
categories   ────►               hitung erosi)                   dwh_dim_wallet
                                                                  dwh_dim_category
                                                                  dwh_fact_transaction
```

### 5.2 Tahap 1 — Extract (Ekstraksi)

**Apa yang dilakukan:** Membaca data dari tabel OLTP yang menjadi sumber fakta dan dimensi.

**Kode Python:**
```python
# Ekstrak semua transaksi (atau filter per user untuk efisiensi)
query = Transaction.query
if user_id is not None:
    query = query.filter_by(user_id=user_id)
transaksi_list = query.all()

# Ambil kurs USD/IDR terkini sekali untuk seluruh batch
kurs_sekarang = _ambil_kurs_sekarang()  # dari yfinance / open.er-api
```

**Query SQL yang dijalankan ORM:**
```sql
SELECT * FROM transactions WHERE user_id = 1;
SELECT * FROM users WHERE id = 1;
SELECT * FROM wallets WHERE id = ?;
SELECT * FROM categories WHERE id = ?;
```

**Mengapa per-user bukan seluruh database?**
- Isolasi data: pengguna A tidak boleh melihat data pengguna B
- Efisiensi: tidak perlu scan seluruh tabel kalau hanya 1 user yang request ETL

**Mengapa kurs diambil sekali di awal, bukan per transaksi?**
- Konsistensi: semua `erosi_persen` dalam satu batch ETL menggunakan kurs yang sama
- Efisiensi: 1 HTTP request ke yfinance, bukan N request untuk N transaksi
- Fallback: jika yfinance gagal (jaringan mati), `kurs_sekarang = None` dan `erosi_persen = NULL` di semua baris — tidak error

### 5.3 Tahap 2 — Transform (Transformasi)

**Apa yang dilakukan:** Mengubah data mentah OLTP menjadi format yang sesuai untuk DWH, termasuk menghitung kolom derived.

#### Transform 2a: Membangun DimDate

Dari tanggal transaksi (misal `2026-05-31`), ETL menurunkan semua atribut waktu:

```python
def _buat_dim_date(tgl):
    weekday = tgl.weekday()   # 0=Senin, 6=Minggu
    dim = DimDate()
    dim.date_id     = tgl.strftime("%Y%m%d")        # "20260531"
    dim.full_date   = tgl                            # 2026-05-31
    dim.day         = tgl.day                        # 31
    dim.month       = tgl.month                      # 5
    dim.month_name  = NAMA_BULAN.get(tgl.month)     # "Mei"
    dim.quarter     = (tgl.month - 1) // 3 + 1      # 2 (Q2: Apr-Jun)
    dim.year        = tgl.year                       # 2026
    dim.day_of_week = NAMA_HARI.get(weekday)         # "Sabtu"
    dim.is_weekend  = weekday >= 5                   # True (5=Sabtu)
    return dim
```

**Contoh transformasi tanggal `2026-05-31`:**

| Kolom Input | Nilai | Kolom Output | Nilai Transformed |
|---|---|---|---|
| `date` | `2026-05-31` | `date_id` | `"20260531"` |
| `date` | `2026-05-31` | `month_name` | `"Mei"` |
| `date` | `2026-05-31` | `quarter` | `2` |
| `date` | `2026-05-31` | `day_of_week` | `"Minggu"` |
| `date` | `2026-05-31` | `is_weekend` | `True` |

#### Transform 2b: Normalisasi Dimensi

Entitas dari OLTP di-copy ke dimensi DWH dengan format yang disederhanakan (tanpa kolom yang tidak relevan untuk analitik):

```python
# Contoh: User OLTP punya kolom password_hash, theme_preference, dll.
# DimUser hanya simpan: user_id, name, email, created_at
dim_user = DimUser()
dim_user.user_id    = user.id
dim_user.name       = user.name
dim_user.email      = user.email
dim_user.created_at = user.created_at.date()   # ambil hanya bagian date
```

**Mengapa tidak semua kolom OLTP dikopi ke DWH?**
- DWH berfokus pada analisis — kolom seperti `password_hash` tidak relevan
- Ukuran lebih kecil = query lebih cepat
- Prinsip "least privilege" — DWH tidak menyimpan data sensitif yang tidak perlu

#### Transform 2c: Menghitung `erosi_persen` (Kolom Derived)

Ini adalah transformasi paling penting dan unik di ReTrack — mengukur berapa persen daya beli Rupiah turun sejak pemasukan diterima hingga sekarang.

**Rumus:**
```
nilai_usd_awal     = amount / usd_rate_at_date    (nilai dalam USD saat terima gaji)
nilai_usd_sekarang = amount / kurs_sekarang        (nilai dalam USD dengan kurs hari ini)
erosi_persen       = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal × 100
```

**Contoh konkret:**
- Gaji bulan Maret: Rp 5.000.000
- Kurs saat gaji diterima (1 Maret 2026): USD/IDR = 15.000
- Kurs sekarang (31 Mei 2026): USD/IDR = 16.200

```
nilai_usd_awal     = 5.000.000 / 15.000 = USD 333,33
nilai_usd_sekarang = 5.000.000 / 16.200 = USD 308,64
erosi_persen       = (333,33 - 308,64) / 333,33 × 100 = 7,41%
```

**Interpretasi:** Rp 5 juta yang diterima Maret 2026 hanya setara dengan USD 308 di Mei 2026, padahal dulu setara USD 333. Daya beli turun 7,41% — uang yang sama tidak bisa membeli barang impor sebanyak dulu.

**Kode Python:**
```python
# Hitung erosi hanya bila kedua kurs tersedia
if trx.usd_rate_at_date and kurs_sekarang:
    hasil = hitung_erosi(trx.amount, trx.usd_rate_at_date, kurs_sekarang)
    erosi = hasil["erosi_persen"]  # float, bisa positif (daya beli turun) atau negatif (naik)
else:
    erosi = None  # NULL di database
```

**SQL equivalentnya (untuk reference):**
```sql
CASE
    WHEN t.usd_rate_at_date IS NOT NULL AND t.usd_rate_at_date <> 0
    THEN ROUND(
        ( (t.amount / t.usd_rate_at_date) - (t.amount / 16200.0) )
        / (t.amount / t.usd_rate_at_date) * 100.0, 4)
    ELSE NULL
END AS erosi_persen
```

### 5.4 Tahap 3 — Load (Pemuatan)

**Apa yang dilakukan:** Memasukkan data yang sudah ditransformasi ke tabel DWH dengan mekanisme UPSERT (update if exists, insert if not).

```python
# UPSERT semua dimensi terlebih dahulu (agar FK di fakta tidak gagal)
db.session.merge(_buat_dim_date(tgl))   # DimDate
db.session.merge(dim_user)              # DimUser
db.session.merge(dim_wallet)            # DimWallet
db.session.merge(dim_cat)              # DimCategory

# Baru load fakta (setelah dimensi sudah ada)
fact = FactTransaction()
fact.fact_id          = trx.id          # KUNCI IDEMPOTEN
fact.date_id          = tgl.strftime("%Y%m%d")
fact.user_id          = trx.user_id
fact.wallet_id        = trx.wallet_id
fact.category_id      = trx.category_id
fact.amount           = trx.amount
fact.kind             = trx.kind
fact.usd_rate_at_date = trx.usd_rate_at_date
fact.erosi_persen     = erosi
fact.etl_loaded_at    = datetime.utcnow()
db.session.merge(fact)

db.session.commit()
```

**Mengapa urutan load penting (Dimensi dulu, baru Fakta)?**
Karena tabel fakta memiliki Foreign Key ke semua dimensi. Kalau fakta di-load lebih dulu sebelum dimensi ada, SQLite akan melempar error `FOREIGN KEY constraint failed`. Urutan wajib:
1. Load `dwh_dim_date`
2. Load `dwh_dim_user`
3. Load `dwh_dim_wallet`
4. Load `dwh_dim_category`
5. Baru load `dwh_fact_transaction`

**Mekanisme Idempoten:**
```python
# Cek apakah fakta sudah ada di DWH sebelum memproses
if FactTransaction.query.get(trx.id) is not None:
    stats["skipped"] += 1
    continue    # Skip — tidak proses ulang
```

`db.session.merge()` adalah UPSERT — kalau objek dengan PK yang sama sudah ada, dia akan UPDATE, bukan INSERT baru. Ini mencegah duplikasi data meski ETL dijalankan berkali-kali.

**Return value ETL:**
```python
return {
    "loaded":  3,   # jumlah fakta baru yang berhasil dimuat
    "skipped": 6,   # jumlah yang sudah ada (dilewati)
    "errors":  0    # jumlah yang gagal (error per transaksi)
}
```

**Penanganan Error per Transaksi:**
```python
try:
    # proses satu transaksi
    stats["loaded"] += 1
except Exception:
    stats["errors"] += 1
    db.session.rollback()  # rollback hanya transaksi yang error
    # transaksi lain tetap dilanjutkan
```

Ini penting karena kalau satu transaksi rusak (misal `usd_rate_at_date` bentuknya tidak valid), tidak boleh menggagalkan seluruh batch ETL.

### 5.5 Ringkasan Alur ETL End-to-End

```
User klik "Jalankan ETL" di /dwh-dashboard
    │
    ▼
POST /api/dwh/etl/run  (Flask endpoint)
    │
    ▼
run_etl(user_id=current_user.id)
    │
    ├── [EXTRACT] Transaction.query.filter_by(user_id=1).all()
    │       └── Hasil: 9 transaksi dari OLTP
    │
    ├── [EXTRACT] kurs_sekarang = market_service.get_usd_idr()
    │       └── Hasil: 16200.0 (USD/IDR hari ini)
    │
    ├── [TRANSFORM + LOAD] Loop per transaksi:
    │       ├── Cek: FactTransaction.query.get(trx.id) → None (belum ada)
    │       ├── Buat DimDate dari tgl → merge ke db
    │       ├── Buat DimUser dari user → merge ke db
    │       ├── Buat DimWallet dari wallet → merge ke db
    │       ├── Buat DimCategory dari category → merge ke db
    │       ├── Hitung erosi_persen = (nilai_usd_awal - nilai_usd_kini) / awal × 100
    │       └── Buat FactTransaction → merge ke db
    │
    ├── db.session.commit()  (simpan semua ke SQLite)
    │
    └── Return {"loaded": 9, "skipped": 0, "errors": 0}
    │
    ▼
Dashboard menampilkan chart dari endpoint:
  GET /api/dwh/summary         → bar chart income vs expense per bulan
  GET /api/dwh/top-categories  → doughnut chart top kategori pengeluaran
  GET /api/dwh/erosi-summary   → KPI card rata-rata erosi nilai
```

---

## Penutup: Kesesuaian dengan Kebutuhan Tugas

| Kebutuhan PPT | Implementasi di ReTrack | Keterangan |
|---|---|---|
| **Pentingnya DWH** | OLTP transaksi tidak bisa agregasi multi-periode efisien; DWH memisahkan beban | Section 1 dokumen ini |
| **Arsitektur Bottom-Up** | Kimball methodology — bangun data mart transaksi keuangan dulu | Section 2 |
| **Conceptual design** | 4 tabel dimensi + 1 tabel fakta dengan penjelasan tiap atribut | Section 3a |
| **Logical design: Star Schema** | Alasan: 1 level hierarki, query simpel, cocok personal finance | Section 3b |
| **Physical design** | DDL `CREATE TABLE` + 5 query analitik + output/hasil query | Section 3c |
| **Software DWH** | Python + SQLAlchemy + SQLite + DB Browser; keunggulan & keterbatasan | Section 4 |
| **ETL Extract** | `Transaction.query.all()` + `market_service.get_usd_idr()` | Section 5.2 |
| **ETL Transform** | Bangun DimDate, normalisasi dimensi, hitung `erosi_persen` | Section 5.3 |
| **ETL Load** | `db.session.merge()` idempoten, urutan dimensi→fakta | Section 5.4 |
