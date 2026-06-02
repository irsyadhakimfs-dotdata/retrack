-- =============================================================================
--  ReTrack — Data Warehouse (STAR SCHEMA)
--  Tugas Project Based Data Warehouse Ke-II — 2025/2026
--
--  File ini adalah ILUSTRASI DESAIN untuk PPT/laporan.
--  Engine: SQLite (buka di "DB Browser for SQLite" untuk eksekusi + screenshot).
--
--  Isi:
--    BAGIAN 0 — (Ilustrasi) Skema sumber OLTP
--    BAGIAN 1 — DDL Star Schema DWH (Physical Design)
--    BAGIAN 2 — Sample data (agar query menghasilkan output untuk screenshot)
--    BAGIAN 3 — ETL: Extract  (SELECT dari OLTP)
--    BAGIAN 4 — ETL: Load     (INSERT/UPSERT ke DWH)
--    BAGIAN 5 — Query Analitik (sumber data untuk chart dashboard)
--
--  Catatan: di aplikasi nyata, tabel berprefix "dwh_" diisi oleh ETL Python
--  (app/services/etl_service.py). SQL di sini menirukan logika tersebut agar
--  bisa dijalankan & di-screenshot langsung di DB Browser.
-- =============================================================================


-- =============================================================================
--  BAGIAN 0 — (ILUSTRASI) SKEMA SUMBER OLTP
--  Ini tabel operasional ReTrack yang menjadi SUMBER ETL. Disertakan agar
--  file SQL bisa berdiri sendiri. Di DB asli tabel ini sudah ada.
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY,
    name       VARCHAR(100),
    email      VARCHAR(200),
    created_at DATETIME
);

CREATE TABLE IF NOT EXISTS wallets (
    id      INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name    VARCHAR(100),
    type    VARCHAR(50)          -- cash / bank / e-wallet
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY,
    name VARCHAR(100),
    kind VARCHAR(10)             -- income / expense
);

CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    wallet_id        INTEGER NOT NULL REFERENCES wallets(id),
    category_id      INTEGER NOT NULL REFERENCES categories(id),
    amount           INTEGER NOT NULL,    -- selalu positif, dalam Rupiah
    kind             VARCHAR(10) NOT NULL,-- income / expense
    date             DATE NOT NULL,
    note             VARCHAR(255),
    created_at       DATETIME,
    usd_rate_at_date FLOAT                -- kurs USD/IDR saat transaksi dibuat
);


-- =============================================================================
--  BAGIAN 1 — DDL STAR SCHEMA DWH  (PHYSICAL DESIGN)
--
--                          dwh_dim_date
--                                |
--   dwh_dim_category ----  dwh_fact_transaction  ---- dwh_dim_wallet
--                                |
--                          dwh_dim_user
-- =============================================================================

DROP TABLE IF EXISTS dwh_fact_transaction;
DROP TABLE IF EXISTS dwh_dim_date;
DROP TABLE IF EXISTS dwh_dim_user;
DROP TABLE IF EXISTS dwh_dim_wallet;
DROP TABLE IF EXISTS dwh_dim_category;

-- ---- DIMENSI: TANGGAL -------------------------------------------------------
-- Dimensi waktu siap pakai untuk slicing (bulan, kuartal, weekend, dll).
CREATE TABLE dwh_dim_date (
    date_id     VARCHAR(8) PRIMARY KEY,   -- format "YYYYMMDD", contoh "20260531"
    full_date   DATE NOT NULL,
    day         INTEGER,
    month       INTEGER,
    month_name  VARCHAR(20),              -- Bahasa Indonesia: "Mei"
    quarter     INTEGER,                  -- 1..4
    year        INTEGER,
    day_of_week VARCHAR(10),              -- Bahasa Indonesia: "Sabtu"
    is_weekend  BOOLEAN                   -- 1 = Sabtu/Minggu
);

-- ---- DIMENSI: PENGGUNA ------------------------------------------------------
CREATE TABLE dwh_dim_user (
    user_id    INTEGER PRIMARY KEY,
    name       VARCHAR(100),
    email      VARCHAR(200),
    created_at DATE
);

-- ---- DIMENSI: DOMPET --------------------------------------------------------
CREATE TABLE dwh_dim_wallet (
    wallet_id INTEGER PRIMARY KEY,
    name      VARCHAR(100),
    type      VARCHAR(50)                 -- cash / bank / e-wallet
);

-- ---- DIMENSI: KATEGORI ------------------------------------------------------
CREATE TABLE dwh_dim_category (
    category_id INTEGER PRIMARY KEY,
    name        VARCHAR(100),
    kind        VARCHAR(10)               -- income / expense
);

-- ---- FAKTA: TRANSAKSI -------------------------------------------------------
-- Grain: 1 baris per transaksi OLTP.
-- fact_id = transactions.id  -> membuat ETL idempoten (tanpa duplikasi baris).
-- Measures: amount (SUM/AVG/COUNT), erosi_persen (AVG).
CREATE TABLE dwh_fact_transaction (
    fact_id          INTEGER PRIMARY KEY,                 -- = transactions.id (BUKAN auto-increment)
    date_id          VARCHAR(8) REFERENCES dwh_dim_date(date_id),
    user_id          INTEGER    REFERENCES dwh_dim_user(user_id),
    wallet_id        INTEGER    REFERENCES dwh_dim_wallet(wallet_id),
    category_id      INTEGER    REFERENCES dwh_dim_category(category_id),
    amount           NUMERIC(15,2),
    kind             VARCHAR(10),                          -- income / expense
    usd_rate_at_date FLOAT,                                -- kurs saat transaksi
    erosi_persen     FLOAT,                                -- kolom turunan (lihat rumus ETL)
    etl_loaded_at    DATETIME
);

-- Index pendukung query agregasi (opsional, mempercepat GROUP BY/filter).
CREATE INDEX idx_fact_date     ON dwh_fact_transaction(date_id);
CREATE INDEX idx_fact_category ON dwh_fact_transaction(category_id);
CREATE INDEX idx_fact_user     ON dwh_fact_transaction(user_id);


-- =============================================================================
--  BAGIAN 2 — SAMPLE DATA OLTP (agar ada output untuk screenshot)
-- =============================================================================

INSERT INTO users (id, name, email, created_at) VALUES
    (1, 'Irsyad Hakim', 'irsyad@example.com', '2026-01-05 09:00:00');

INSERT INTO wallets (id, user_id, name, type) VALUES
    (1, 1, 'Dompet Tunai', 'cash'),
    (2, 1, 'Rekening BCA', 'bank');

INSERT INTO categories (id, name, kind) VALUES
    (1, 'Gaji',         'income'),
    (2, 'Makan',        'expense'),
    (3, 'Transportasi', 'expense'),
    (4, 'Hiburan',      'expense');

-- Transaksi: income punya usd_rate_at_date (dasar erosi), expense boleh isi juga.
INSERT INTO transactions
    (id, user_id, wallet_id, category_id, amount, kind, date, note, usd_rate_at_date) VALUES
    (1, 1, 2, 1, 5000000, 'income',  '2026-03-01', 'Gaji Maret', 15000),
    (2, 1, 1, 2,  150000, 'expense', '2026-03-03', 'Makan siang', NULL),
    (3, 1, 1, 3,   50000, 'expense', '2026-03-07', 'Ojek',        NULL),
    (4, 1, 2, 1, 5000000, 'income',  '2026-04-01', 'Gaji April',  15500),
    (5, 1, 1, 2,  200000, 'expense', '2026-04-05', 'Makan',       NULL),
    (6, 1, 1, 4,  120000, 'expense', '2026-04-12', 'Nonton',      NULL),
    (7, 1, 2, 1, 5000000, 'income',  '2026-05-01', 'Gaji Mei',    16000),
    (8, 1, 1, 2,  175000, 'expense', '2026-05-09', 'Makan',       NULL),
    (9, 1, 1, 3,   80000, 'expense', '2026-05-16', 'Bensin',      NULL);


-- =============================================================================
--  BAGIAN 3 — ETL: EXTRACT (baca data sumber dari OLTP)
-- =============================================================================

-- 3.1 Ekstrak transaksi (sumber tabel fakta)
SELECT t.id, t.user_id, t.wallet_id, t.category_id,
       t.amount, t.kind, t.date, t.usd_rate_at_date
FROM transactions t
WHERE t.user_id = 1;

-- 3.2 Ekstrak referensi dimensi
SELECT id, name, email, created_at FROM users;
SELECT id, name, type FROM wallets;
SELECT id, name, kind FROM categories;


-- =============================================================================
--  BAGIAN 4 — ETL: TRANSFORM + LOAD (muat ke tabel DWH, idempoten)
--
--  Catatan transform:
--   * dim_date dibangun dari tiap tanggal unik transaksi (di app via Python).
--     Di SQLite, strftime dipakai untuk menurunkan atribut waktu.
--   * erosi_persen dihitung dengan rumus daya beli (lihat 4.5).
--   * "INSERT OR REPLACE" = UPSERT -> menjalankan ulang tidak menduplikasi.
-- =============================================================================

-- 4.1 LOAD dim_date — turunkan atribut dari tanggal unik transaksi
--     (month_name & day_of_week di app diisi Bahasa Indonesia; di sini diset via CASE)
INSERT OR REPLACE INTO dwh_dim_date
    (date_id, full_date, day, month, month_name, quarter, year, day_of_week, is_weekend)
SELECT
    strftime('%Y%m%d', t.date)                         AS date_id,
    t.date                                             AS full_date,
    CAST(strftime('%d', t.date) AS INTEGER)            AS day,
    CAST(strftime('%m', t.date) AS INTEGER)            AS month,
    CASE CAST(strftime('%m', t.date) AS INTEGER)
        WHEN 1 THEN 'Januari'  WHEN 2 THEN 'Februari' WHEN 3 THEN 'Maret'
        WHEN 4 THEN 'April'    WHEN 5 THEN 'Mei'       WHEN 6 THEN 'Juni'
        WHEN 7 THEN 'Juli'     WHEN 8 THEN 'Agustus'   WHEN 9 THEN 'September'
        WHEN 10 THEN 'Oktober' WHEN 11 THEN 'November' WHEN 12 THEN 'Desember'
    END                                                AS month_name,
    (CAST(strftime('%m', t.date) AS INTEGER) - 1) / 3 + 1 AS quarter,
    CAST(strftime('%Y', t.date) AS INTEGER)            AS year,
    -- strftime('%w'): 0=Minggu, 1=Senin, ... 6=Sabtu
    CASE strftime('%w', t.date)
        WHEN '0' THEN 'Minggu' WHEN '1' THEN 'Senin'  WHEN '2' THEN 'Selasa'
        WHEN '3' THEN 'Rabu'   WHEN '4' THEN 'Kamis'  WHEN '5' THEN 'Jumat'
        WHEN '6' THEN 'Sabtu'
    END                                                AS day_of_week,
    CASE WHEN strftime('%w', t.date) IN ('0','6') THEN 1 ELSE 0 END AS is_weekend
FROM (SELECT DISTINCT date FROM transactions) t;

-- 4.2 LOAD dim_user
INSERT OR REPLACE INTO dwh_dim_user (user_id, name, email, created_at)
SELECT id, name, email, DATE(created_at) FROM users;

-- 4.3 LOAD dim_wallet
INSERT OR REPLACE INTO dwh_dim_wallet (wallet_id, name, type)
SELECT id, name, type FROM wallets;

-- 4.4 LOAD dim_category
INSERT OR REPLACE INTO dwh_dim_category (category_id, name, kind)
SELECT id, name, kind FROM categories;

-- 4.5 LOAD fact_transaction (+ hitung erosi_persen)
--     Rumus erosi (daya beli Rupiah terhadap USD), asumsi kurs_sekarang = 16200:
--        nilai_usd_awal     = amount / usd_rate_at_date
--        nilai_usd_sekarang = amount / kurs_sekarang
--        erosi_persen       = (awal - sekarang) / awal * 100
--     Positif = daya beli turun. Hanya dihitung bila usd_rate_at_date tersedia.
INSERT OR REPLACE INTO dwh_fact_transaction
    (fact_id, date_id, user_id, wallet_id, category_id,
     amount, kind, usd_rate_at_date, erosi_persen, etl_loaded_at)
SELECT
    t.id,
    strftime('%Y%m%d', t.date),
    t.user_id,
    t.wallet_id,
    t.category_id,
    t.amount,
    t.kind,
    t.usd_rate_at_date,
    CASE
        WHEN t.usd_rate_at_date IS NOT NULL AND t.usd_rate_at_date <> 0
        THEN ROUND(
            ( (t.amount / t.usd_rate_at_date) - (t.amount / 16200.0) )
            / (t.amount / t.usd_rate_at_date) * 100.0, 4)
        ELSE NULL
    END                                              AS erosi_persen,
    CURRENT_TIMESTAMP
FROM transactions t;
-- ^ Jalankan ulang query ini -> baris tidak bertambah (idempoten, PK = t.id).


-- =============================================================================
--  BAGIAN 5 — QUERY ANALITIK DWH  (sumber data untuk chart dashboard)
-- =============================================================================

-- 5.1 (Bar chart) Pemasukan vs Pengeluaran per bulan untuk satu tahun
--     -> endpoint GET /api/dwh/summary?year=2026
SELECT d.month, d.month_name, f.kind, SUM(f.amount) AS total
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE f.user_id = 1 AND d.year = 2026
GROUP BY d.month, d.month_name, f.kind
ORDER BY d.month;

-- 5.2 (Doughnut chart) Top 5 kategori PENGELUARAN
--     -> endpoint GET /api/dwh/top-categories?kind=expense
SELECT c.name AS category,
       SUM(f.amount)      AS total,
       COUNT(f.fact_id)   AS jumlah_transaksi
FROM dwh_fact_transaction f
JOIN dwh_dim_category c ON f.category_id = c.category_id
WHERE f.user_id = 1 AND f.kind = 'expense'
GROUP BY c.name
ORDER BY total DESC
LIMIT 5;

-- 5.3 (KPI card) Rata-rata erosi nilai pemasukan
--     -> endpoint GET /api/dwh/erosi-summary
SELECT ROUND(AVG(f.erosi_persen), 4) AS avg_erosi_persen,
       COUNT(f.fact_id)              AS total_income_transactions
FROM dwh_fact_transaction f
WHERE f.user_id = 1
  AND f.kind = 'income'
  AND f.erosi_persen IS NOT NULL;

-- 5.4 (Analisis tambahan) Ringkasan net per kuartal
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

-- 5.5 (Analisis tambahan) Pengeluaran: weekend vs weekday
SELECT CASE WHEN d.is_weekend = 1 THEN 'Akhir Pekan' ELSE 'Hari Kerja' END AS tipe_hari,
       SUM(f.amount) AS total_pengeluaran,
       COUNT(f.fact_id) AS jumlah
FROM dwh_fact_transaction f
JOIN dwh_dim_date d ON f.date_id = d.date_id
WHERE f.user_id = 1 AND f.kind = 'expense'
GROUP BY d.is_weekend;

-- =============================================================================
--  SELESAI.
--  Untuk screenshot PPT: jalankan BAGIAN 1 (DDL), BAGIAN 2 (data),
--  BAGIAN 4 (ETL load), lalu tiap query di BAGIAN 5, dan tangkap output-nya.
-- =============================================================================
