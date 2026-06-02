# Proses ETL di ReTrack — Extract, Transform, Load

Dokumen ini menjelaskan **seluruh alur ETL** yang ada di program: dari transaksi
OLTP ke lapisan Data Warehouse (DWH) star schema, termasuk kalkulasi erosi daya
beli. Halaman `/dwh-dashboard` sudah dihapus, tetapi **ETL API dan service-nya
tetap berjalan** dan dipakai oleh fitur erosi nilai.

---

## Gambaran Umum Arsitektur

```
OLTP (SQLite)                   DWH (tabel dwh_* di DB yang sama)
─────────────────               ──────────────────────────────────
transactions      ──► ETL ──►   dwh_fact_transaction   (fakta)
users             ──► ETL ──►   dwh_dim_user           (dimensi)
wallets           ──► ETL ──►   dwh_dim_wallet         (dimensi)
categories        ──► ETL ──►   dwh_dim_category       (dimensi)
(tanggal trx)     ──► ETL ──►   dwh_dim_date           (dimensi)
```

Pola yang dipakai adalah **Star Schema**: satu tabel fakta yang dikelilingi
beberapa tabel dimensi. ETL bersifat **idempoten** — menjalankan dua kali tidak
menghasilkan duplikasi baris karena `fact_id = transaction.id` OLTP.

---

## 1. Model DWH (Star Schema)

**File:** `app/models/dwh.py`

### 1.1 Tabel Dimensi

#### DimDate — `dwh_dim_date`
Menyimpan atribut waktu dari setiap tanggal unik transaksi.

```python
class DimDate(db.Model):
    __tablename__ = "dwh_dim_date"

    date_id     = db.Column(db.String(8), primary_key=True)  # format "YYYYMMDD"
    full_date   = db.Column(db.Date, nullable=False)
    day         = db.Column(db.Integer)
    month       = db.Column(db.Integer)
    month_name  = db.Column(db.String(20))   # "Januari" … "Desember"
    quarter     = db.Column(db.Integer)      # 1–4
    year        = db.Column(db.Integer)
    day_of_week = db.Column(db.String(10))   # "Senin" … "Minggu"
    is_weekend  = db.Column(db.Boolean)
```

Konstanta pendukung (bahasa Indonesia):
```python
NAMA_BULAN = {1: "Januari", 2: "Februari", ..., 12: "Desember"}
NAMA_HARI  = {0: "Senin",   1: "Selasa",   ..., 6:  "Minggu"}
```

#### DimUser — `dwh_dim_user`
Salinan ringkas data pengguna dari tabel `users` OLTP.

```python
class DimUser(db.Model):
    __tablename__ = "dwh_dim_user"

    user_id    = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    email      = db.Column(db.String(200))
    created_at = db.Column(db.Date)
```

#### DimWallet — `dwh_dim_wallet`
Salinan ringkas data dompet dari tabel `wallets` OLTP.

```python
class DimWallet(db.Model):
    __tablename__ = "dwh_dim_wallet"

    wallet_id = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100))
    type      = db.Column(db.String(50))
```

#### DimCategory — `dwh_dim_category`
Salinan ringkas data kategori dari tabel `categories` OLTP.

```python
class DimCategory(db.Model):
    __tablename__ = "dwh_dim_category"

    category_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100))
    kind        = db.Column(db.String(10))   # "income" atau "expense"
```

### 1.2 Tabel Fakta

#### FactTransaction — `dwh_fact_transaction`
Satu baris per transaksi yang sudah di-ETL. Kolom `erosi_persen` adalah
hasil kalkulasi erosi daya beli (diisi saat ETL bila kurs tersedia).

```python
class FactTransaction(db.Model):
    __tablename__ = "dwh_fact_transaction"

    fact_id          = db.Column(db.Integer, primary_key=True, autoincrement=False)
    date_id          = db.Column(db.String(8),  db.ForeignKey("dwh_dim_date.date_id"))
    user_id          = db.Column(db.Integer,    db.ForeignKey("dwh_dim_user.user_id"))
    wallet_id        = db.Column(db.Integer,    db.ForeignKey("dwh_dim_wallet.wallet_id"))
    category_id      = db.Column(db.Integer,    db.ForeignKey("dwh_dim_category.category_id"), nullable=True)
    amount           = db.Column(db.Numeric(15, 2))
    kind             = db.Column(db.String(10))           # "income" atau "expense"
    usd_rate_at_date = db.Column(db.Float, nullable=True) # kurs saat transaksi dicatat
    erosi_persen     = db.Column(db.Float, nullable=True) # hasil ETL Transform
    etl_loaded_at    = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 2. Service ETL

**File:** `app/services/etl_service.py`

Fungsi utama: `run_etl(user_id=None)` — menjalankan tiga fase ETL secara
berurutan untuk setiap transaksi.

### 2.1 EXTRACT — Baca data dari OLTP

```python
# Query transaksi dari tabel OLTP (bisa difilter per user)
query = Transaction.query
if user_id is not None:
    query = query.filter_by(user_id=user_id)
transaksi_list = query.all()

# Ambil kurs USD/IDR terkini sekali untuk seluruh batch
kurs_sekarang = _ambil_kurs_sekarang()
```

Fungsi pembantu pengambil kurs:
```python
def _ambil_kurs_sekarang():
    try:
        from app.services.market_service import get_usd_idr
        result = get_usd_idr()
        if result and result.get("rate"):
            return float(result["rate"])
    except Exception:
        pass
    return None   # gagal jaringan → ETL tetap jalan, erosi_persen = None
```

### 2.2 TRANSFORM — Hitung erosi & bangun objek dimensi

**Cek idempoten** (skip bila fakta sudah ada):
```python
if FactTransaction.query.get(trx.id) is not None:
    stats["skipped"] += 1
    continue
```

**Bangun DimDate** dari tanggal transaksi:
```python
def _buat_dim_date(tgl):
    weekday = tgl.weekday()   # 0=Senin … 6=Minggu
    dim = DimDate()
    dim.date_id     = tgl.strftime("%Y%m%d")
    dim.full_date   = tgl
    dim.day         = tgl.day
    dim.month       = tgl.month
    dim.month_name  = NAMA_BULAN.get(tgl.month, str(tgl.month))
    dim.quarter     = (tgl.month - 1) // 3 + 1
    dim.year        = tgl.year
    dim.day_of_week = NAMA_HARI.get(weekday, str(weekday))
    dim.is_weekend  = weekday >= 5
    return dim
```

**Hitung erosi daya beli** (kalkulasi utama fitur erosi nilai):
```python
erosi = None
if trx.usd_rate_at_date and kurs_sekarang:
    hasil = hitung_erosi(trx.amount, trx.usd_rate_at_date, kurs_sekarang)
    if hasil:
        erosi = hasil["erosi_persen"]
```

Rumus erosi (dari `app/services/erosion_service.py`):
```python
def hitung_erosi(jumlah_rupiah, kurs_awal, kurs_sekarang):
    nilai_usd_awal     = jumlah_rupiah / kurs_awal
    nilai_usd_sekarang = jumlah_rupiah / kurs_sekarang
    erosi_persen       = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal * 100
    # Positif = daya beli turun (Rupiah melemah)
    # Negatif = daya beli naik (Rupiah menguat)
    return {
        "nilai_usd_awal":     round(nilai_usd_awal, 4),
        "nilai_usd_sekarang": round(nilai_usd_sekarang, 4),
        "erosi_persen":       round(erosi_persen, 4),
    }
```

### 2.3 LOAD — Tulis ke tabel DWH

Semua objek dimensi di-`merge` (insert-or-update) sebelum fakta ditulis:

```python
db.session.merge(_buat_dim_date(tgl))   # dwh_dim_date

dim_user = DimUser()
dim_user.user_id    = user.id
dim_user.name       = user.name
dim_user.email      = user.email
dim_user.created_at = user.created_at.date() if user.created_at else None
db.session.merge(dim_user)              # dwh_dim_user

dim_wallet = DimWallet()
dim_wallet.wallet_id = wallet.id
dim_wallet.name      = wallet.name
dim_wallet.type      = wallet.type
db.session.merge(dim_wallet)            # dwh_dim_wallet

dim_cat = DimCategory()
dim_cat.category_id = cat.id
dim_cat.name        = cat.name
dim_cat.kind        = cat.kind
db.session.merge(dim_cat)               # dwh_dim_category

# Fakta utama (gabungan semua dimensi + hasil transform)
fact = FactTransaction()
fact.fact_id          = trx.id
fact.date_id          = tgl.strftime("%Y%m%d")
fact.user_id          = trx.user_id
fact.wallet_id        = trx.wallet_id
fact.category_id      = trx.category_id
fact.amount           = trx.amount
fact.kind             = trx.kind
fact.usd_rate_at_date = trx.usd_rate_at_date
fact.erosi_persen     = erosi               # hasil dari hitung_erosi()
fact.etl_loaded_at    = datetime.utcnow()
db.session.merge(fact)                  # dwh_fact_transaction

db.session.commit()
```

### 2.4 Return Value

```python
stats = {"loaded": int, "skipped": int, "errors": int}
```

| Key | Arti |
|-----|------|
| `loaded` | Baris baru yang berhasil dimasukkan ke DWH |
| `skipped` | Baris yang dilewati karena sudah ada di DWH (idempoten) |
| `errors` | Jumlah transaksi yang gagal diproses (rollback per-baris) |

---

## 3. API Endpoint ETL

**File:** `app/api/dwh.py` — prefix URL: `/api/dwh`

### POST `/api/dwh/etl/run`
Menjalankan ETL untuk pengguna yang sedang login.

```python
@bp.route("/etl/run", methods=["POST"])
@login_required
def etl_run():
    stats = run_etl(user_id=current_user.id)
    return jsonify({"ok": True, "data": stats})
```

Contoh respons:
```json
{
  "ok": true,
  "data": {"loaded": 42, "skipped": 10, "errors": 0}
}
```

### GET `/api/dwh/summary?year=2026`
Total income & expense per bulan dari `FactTransaction` DWH.

```python
rows = (
    db.session.query(
        DimDate.month,
        DimDate.month_name,
        FactTransaction.kind,
        func.sum(FactTransaction.amount).label("total"),
    )
    .join(DimDate, FactTransaction.date_id == DimDate.date_id)
    .filter(FactTransaction.user_id == current_user.id)
    .filter(DimDate.year == tahun)
    .group_by(DimDate.month, DimDate.month_name, FactTransaction.kind)
    .order_by(DimDate.month)
    .all()
)
```

### GET `/api/dwh/top-categories?months=3&kind=expense`
Top 5 kategori berdasarkan total transaksi N bulan terakhir.

```python
rows = (
    db.session.query(
        DimCategory.name,
        func.sum(FactTransaction.amount).label("total"),
        func.count(FactTransaction.fact_id).label("count"),
    )
    .join(DimCategory, FactTransaction.category_id == DimCategory.category_id)
    .filter(FactTransaction.user_id == current_user.id)
    .filter(FactTransaction.kind == kind)
    .filter(FactTransaction.date_id >= cutoff_id)
    .group_by(DimCategory.name)
    .order_by(func.sum(FactTransaction.amount).desc())
    .limit(5)
    .all()
)
```

### GET `/api/dwh/erosi-summary`
Rata-rata erosi daya beli dari seluruh transaksi income user.

```python
row = (
    db.session.query(
        func.avg(FactTransaction.erosi_persen).label("avg_erosi"),
        func.count(FactTransaction.fact_id).label("total"),
    )
    .filter(FactTransaction.user_id == current_user.id)
    .filter(FactTransaction.kind == "income")
    .filter(FactTransaction.erosi_persen.isnot(None))
    .first()
)
```

---

## 4. Skema Migrasi Database

**File:** `migrations/versions/8df4d27d7c4b_add_dwh_star_schema_tables.py`

Migrasi ini membuat kelima tabel DWH sekaligus. Tabel-tabel ini juga
terdaftar di `app/models/__init__.py` agar Flask-Migrate mendeteksinya:

```python
from app.models.dwh import DimDate, DimUser, DimWallet, DimCategory, FactTransaction
```

Dan di `app/__init__.py` dalam `create_app()`:
```python
from app.models import (
    ...,
    DimDate, DimUser, DimWallet, DimCategory, FactTransaction,
)
```

---

## 5. Alur Lengkap (Ringkasan)

```
[User klik "Jalankan ETL"]
        │
        ▼
POST /api/dwh/etl/run
        │
        ▼
run_etl(user_id)                    ← app/services/etl_service.py
        │
        ├─ EXTRACT ─► Transaction.query.filter_by(user_id=...)
        │
        ├─ TRANSFORM (per transaksi)
        │       ├─ Skip bila fact_id sudah ada   (idempoten)
        │       ├─ Bangun DimDate dari tgl.strftime("%Y%m%d")
        │       ├─ Copy DimUser / DimWallet / DimCategory dari OLTP
        │       └─ hitung_erosi(amount, usd_rate_at_date, kurs_sekarang)
        │               └─ app/services/erosion_service.py
        │
        └─ LOAD ──► db.session.merge(...) + db.session.commit()
                        ├─ dwh_dim_date
                        ├─ dwh_dim_user
                        ├─ dwh_dim_wallet
                        ├─ dwh_dim_category
                        └─ dwh_fact_transaction (+ erosi_persen)
```

---

## 6. File Terkait

| File | Peran |
|------|-------|
| `app/models/dwh.py` | Definisi 5 tabel DWH (star schema) |
| `app/services/etl_service.py` | Logika ETL penuh (Extract → Transform → Load) |
| `app/services/erosion_service.py` | Kalkulasi erosi daya beli (`hitung_erosi`) |
| `app/services/market_service.py` | Sumber kurs USD/IDR terkini untuk ETL |
| `app/api/dwh.py` | REST API endpoint: `/api/dwh/etl/run`, `/summary`, `/top-categories`, `/erosi-summary` |
| `migrations/versions/8df4d27d7c4b_*.py` | Migrasi Alembic untuk tabel DWH |
| `dwh/dwh_star_schema.sql` | Definisi SQL star schema (referensi) |
| `tests/test_dwh.py` | Test suite untuk ETL dan query DWH |
