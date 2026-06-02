# 06 — Perubahan 4: DWH Integration + App Polish

> **Dokumen ini adalah spesifikasi lengkap Perubahan 4 untuk agent Claude Code baru.**
> Baca sampai habis sebelum mengerjakan apa pun. Kerjakan berurutan sesuai urutan sub-fase.

---

## Konteks: Mengapa Perubahan Ini Ada

Pemilik proyek adalah mahasiswa Data Science yang mengambil mata kuliah **Data Warehouse**.
Tugas Project II mewajibkan perancangan Data Warehouse lengkap dengan:
- Conceptual design (tabel fakta & dimensi)
- Logical design (star/snowflake/galaxy schema + alasan)
- Physical design (DDL query + output screenshot)
- Proses ETL (extract, transform, load + screenshot)
- Visualisasi data / digital dashboard
- Deadline PPT: **31 Mei 2026 pukul 22.00** · Presentasi: **3 Juni 2026**

**Solusi:** ReTrack digunakan sebagai topik tugas DWH. Aplikasi ini sudah punya data OLTP
(transaksi, wallet, kategori, budget, goals). Perubahan 4 menambahkan lapisan DWH
(tabel dimensi + fakta, ETL script, endpoint query DWH) dan screenshot untuk PPT.

---

## Tiga Keputusan Final (TIDAK ditawar ulang)

1. **DWH schema = Star Schema.** Dimensi hanya 1 level (tidak perlu normalisasi ke snowflake),
   query simpel, cocok untuk personal finance tracker berskala kecil.
2. **DWH disimpan di database yang SAMA** (`refinance_dev.db`) sebagai tabel terpisah
   dengan prefix `dwh_`. Tidak perlu DB baru; migrasi lebih mudah.
3. **Nama teknis `refinance` TETAP.** Jangan rename folder/package/DB.

---

## Arsitektur DWH yang Akan Dibangun

### Star Schema ReTrack

```
                    ┌──────────────┐
                    │  dim_date    │
                    │─────────────│
                    │ date_id (PK) │
                    │ full_date    │
                    │ day          │
                    │ month        │
                    │ month_name   │
                    │ quarter      │
                    │ year         │
                    │ day_of_week  │
                    │ is_weekend   │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴──────────────┐    ┌──────────────────┐
│ dim_category │    │  fact_transaction   │    │   dim_wallet     │
│─────────────│    │─────────────────────│    │─────────────────│
│category_id  ├────┤ fact_id (PK)        ├────┤ wallet_id (PK)  │
│name         │    │ date_id (FK)        │    │ name            │
│kind         │    │ user_id (FK)        │    │ type            │
└─────────────┘    │ wallet_id (FK)      │    └──────────────────┘
                    │ category_id (FK)    │
┌──────────────┐    │ amount (DECIMAL)    │
│  dim_user    │    │ kind (income/exp)   │
│─────────────│    │ usd_rate_at_date    │
│ user_id (PK)├────┤ erosi_persen        │
│ name        │    └─────────────────────┘
│ email       │
│ created_at  │    Tabel Fakta Ukuran (Measures):
└─────────────┘    • amount → SUM, AVG, COUNT
                    • erosi_persen → AVG
                    • Derived: total_income, total_expense, selisih
```

### Kenapa Star Schema?
- Dimensi hanya punya 1 level hierarki (tidak ada sub-dimensi) → normalisasi ke snowflake tidak perlu
- Query lebih cepat (lebih sedikit JOIN)
- Mudah dipahami untuk PPT

### Pendekatan Arsitektur: Bottom-Up (Kimball)
Bangun data mart dulu dari transaksi keuangan (paling kritis), baru bisa dikembangkan ke
tabel fakta lain (budget facts, goal facts) kalau perlu.

---

## Sub-Fase Pengerjaan

### 4a — Model DWH (tabel dimensi + fakta)

**File baru:** `app/models/dwh.py`

Buat 5 model SQLAlchemy:

```python
class DimDate(db.Model):
    __tablename__ = "dwh_dim_date"
    date_id   = db.Column(db.String(8), primary_key=True)  # "20260531"
    full_date = db.Column(db.Date, nullable=False)
    day       = db.Column(db.Integer)
    month     = db.Column(db.Integer)
    month_name= db.Column(db.String(20))  # "Mei"
    quarter   = db.Column(db.Integer)
    year      = db.Column(db.Integer)
    day_of_week = db.Column(db.String(10))  # "Sabtu"
    is_weekend  = db.Column(db.Boolean)

class DimUser(db.Model):
    __tablename__ = "dwh_dim_user"
    user_id    = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    email      = db.Column(db.String(200))
    created_at = db.Column(db.Date)

class DimWallet(db.Model):
    __tablename__ = "dwh_dim_wallet"
    wallet_id = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100))
    type      = db.Column(db.String(50))

class DimCategory(db.Model):
    __tablename__ = "dwh_dim_category"
    category_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100))
    kind        = db.Column(db.String(10))   # "income" / "expense"

class FactTransaction(db.Model):
    __tablename__ = "dwh_fact_transaction"
    fact_id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_id         = db.Column(db.String(8),   db.ForeignKey("dwh_dim_date.date_id"))
    user_id         = db.Column(db.Integer,     db.ForeignKey("dwh_dim_user.user_id"))
    wallet_id       = db.Column(db.Integer,     db.ForeignKey("dwh_dim_wallet.wallet_id"))
    category_id     = db.Column(db.Integer,     db.ForeignKey("dwh_dim_category.category_id"),
                                nullable=True)
    amount          = db.Column(db.Numeric(15, 2))
    kind            = db.Column(db.String(10))
    usd_rate_at_date= db.Column(db.Float, nullable=True)
    erosi_persen    = db.Column(db.Float, nullable=True)
    etl_loaded_at   = db.Column(db.DateTime, default=datetime.utcnow)
```

**Daftarkan di `app/models/__init__.py`** dan buat migrasi:
```bash
flask db migrate -m "add dwh star schema tables"
flask db upgrade
```

---

### 4b — ETL Service (`app/services/etl_service.py`)

File baru. Logika ETL murni (tidak ada logika tampilan):

```python
def run_etl(user_id=None):
    """
    Jalankan ETL penuh: extract dari OLTP → transform → load ke DWH.
    Jika user_id diberikan, hanya proses data user tersebut.
    Kembalikan dict {"loaded": int, "skipped": int, "errors": int}.
    """
```

**Langkah ETL:**

1. **Extract** — baca dari tabel OLTP:
   - `Transaction` (sumber fakta)
   - `User`, `Wallet`, `Category` (sumber dimensi)

2. **Transform** — normalisasi data:
   - Bangun `DimDate` dari setiap tanggal unik transaksi
     (date_id = `"YYYYMMDD"`, isi semua atribut waktu dalam Bahasa Indonesia)
   - Bangun `DimUser` / `DimWallet` / `DimCategory` dari OLTP (upsert — tidak duplikasi)
   - Hitung `erosi_persen` bila `usd_rate_at_date` tersedia dan kurs sekarang ada

3. **Load** — INSERT OR REPLACE ke tabel DWH:
   - Gunakan `db.session.merge()` untuk upsert (tidak INSERT duplikat)
   - Skip fakta yang sudah ada (cek berdasarkan `fact_id = transaction.id`)
   - Catat `etl_loaded_at`

4. **Return** stats untuk logging & endpoint

**Penting:**
- Bungkus dalam `try/except`, rollback bila error
- ETL tidak boleh mengubah data OLTP sama sekali
- `fact_id` = `transaction.id` dari OLTP (bukan auto-increment baru) agar idempotent

---

### 4c — Endpoint DWH API (`app/api/dwh.py`)

Blueprint baru `dwh` dengan prefix `/api/dwh`. Semua endpoint `@login_required`.

```
POST /api/dwh/etl/run
→ Jalankan ETL untuk current_user, return stats {"loaded", "skipped", "errors"}

GET /api/dwh/summary?year=2026
→ Total income & expense per bulan untuk tahun N (dari FactTransaction)
→ {"ok": true, "data": [{"month": 5, "month_name": "Mei", "income": ..., "expense": ...}]}

GET /api/dwh/top-categories?months=3&kind=expense
→ Top 5 kategori pengeluaran N bulan terakhir (dari FactTransaction JOIN DimCategory)
→ {"ok": true, "data": [{"category": "Makan", "total": 1500000, "count": 12}]}

GET /api/dwh/erosi-summary
→ Rata-rata erosi nilai semua income user (dari FactTransaction WHERE kind='income')
→ {"ok": true, "data": {"avg_erosi_persen": 4.2, "total_income_transactions": 15}}
```

Daftarkan blueprint di `app/api/__init__.py`.

---

### 4d — Halaman DWH Dashboard (opsional tapi direkomendasikan untuk PPT)

Halaman baru `/dwh-dashboard` (view + template) yang menampilkan:
- Tombol "Jalankan ETL" (POST ke `/api/dwh/etl/run`)
- Chart bar: income vs expense per bulan (dari `/api/dwh/summary`)
- Chart doughnut: top kategori pengeluaran (dari `/api/dwh/top-categories`)
- Card: rata-rata erosi nilai (dari `/api/dwh/erosi-summary`)
- Label "Data Warehouse Mode" agar jelas ini beda dari OLTP dashboard

Tambahkan link ke sidebar (`base.html`): ikon `storage`, label "DWH Dashboard".

---

### 4e — Test (`tests/test_dwh.py`)

Test minimal:
- `test_etl_run_sukses` — POST `/api/dwh/etl/run`, assert stats["loaded"] >= 0
- `test_dwh_summary` — GET `/api/dwh/summary`, assert struktur respons benar
- `test_top_categories` — GET `/api/dwh/top-categories`, assert list
- `test_etl_idempoten` — jalankan ETL 2x, assert jumlah baris tidak bertambah

---

## Mapping ke Tugas DWH (untuk PPT)

| Kebutuhan PPT | Sumber di ReTrack |
|---|---|
| **Pentingnya DWH** | OLTP transaksi tidak bisa aggregate multi-periode efisien; DWH memisahkan beban query analitik |
| **Arsitektur Bottom-Up** | Bangun data mart transaksi dulu (Kimball methodology) |
| **Conceptual design** | Diagram star schema di atas (tabel fakta + 4 dimensi) |
| **Logical design: Star Schema** | Alasan: 1 level hierarki per dimensi, query simpel, cocok data keuangan personal |
| **Physical design** | DDL CREATE TABLE (output dari `flask db upgrade` + manual DDL dari `dwh.py`) |
| **Software DWH** | Python + SQLAlchemy + SQLite (DWH embedded); keunggulan: zero-config, gratis |
| **ETL Extract** | Baca dari tabel OLTP (`transactions`, `users`, `wallets`, `categories`) |
| **ETL Transform** | Generate DimDate attributes, normalisasi dimensi, hitung erosi_persen |
| **ETL Load** | `db.session.merge()` ke tabel `dwh_*`; idempotent |
| **Software Visualisasi** | Chart.js (sudah ada di ReTrack) — halaman DWH Dashboard |
| **Screenshot query + output** | Ambil dari endpoint `/api/dwh/*` di browser / Postman |

---

## Perubahan App yang Sudah Dilakukan Sebelum Perubahan 4

(Tidak perlu diulang — sudah selesai)

| Perubahan | Status |
|---|---|
| Rename tampilan ReFinance → ReTrack | ✅ Done |
| Logo + favicon | ✅ Done |
| Market via yfinance + linechart 6 bulan | ✅ Done |
| Trend analysis default 6 → 2 bulan (configurable via `TREND_DEFAULT_MONTHS`) | ✅ Done |

---

## Aturan Wajib (dari CLAUDE.md — TIDAK BOLEH dilanggar)

1. **Pemisahan lapisan:** `models/` hanya definisi tabel · `api/` selalu JSON · `services/` logika bisnis · `views/` render HTML
2. **Komentar Python `#` Bahasa Indonesia** yang jelas
3. **Semua teks UI Bahasa Indonesia**
4. **Jangan hardcode** — semua config via `.env` + `app/config.py`
5. **Test untuk setiap fitur baru** di `tests/`
6. **Jangan refactor di luar scope** perubahan ini

---

## Definition of Done Perubahan 4

- [ ] Tabel `dwh_dim_date`, `dwh_dim_user`, `dwh_dim_wallet`, `dwh_dim_category`, `dwh_fact_transaction` tersedia di DB
- [ ] `POST /api/dwh/etl/run` berhasil load data transaksi ke DWH
- [ ] `GET /api/dwh/summary` return data benar
- [ ] `GET /api/dwh/top-categories` return top kategori
- [ ] Halaman `/dwh-dashboard` tampil dengan chart (opsional tapi direkomendasikan untuk screenshot PPT)
- [ ] `pytest -q` PASS semua (termasuk `tests/test_dwh.py`)
- [ ] DDL screenshot tersedia untuk PPT

---

## Commit

```
feat(dwh): tambah lapisan data warehouse star schema + ETL + dashboard
```

---

## Catatan untuk Agent

1. Baca `CLAUDE.md` + `PROGRESS.md` dulu sebelum mulai
2. Ikuti urutan 4a → 4b → 4c → 4d → 4e
3. Setelah tiap sub-fase: `pytest -q`, laporkan hasil
4. **Jangan commit otomatis** kecuali diminta user
5. Untuk Perubahan 4d (halaman dashboard DWH): tampilkan angka & chart yang bisa di-screenshot untuk PPT mahasiswa
6. Perubahan 4 TIDAK mengubah tabel OLTP yang sudah ada — DWH adalah lapisan tambahan
