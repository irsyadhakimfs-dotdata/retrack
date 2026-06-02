# Model Data Warehouse (DWH) — Star Schema ReTrack
# Semua tabel berprefix "dwh_" dan disimpan di DB yang sama dengan OLTP.
# Tabel ini HANYA dibaca/ditulis oleh ETL service; OLTP tidak pernah disentuh.

from datetime import datetime
from app.extensions import db

# Nama bulan dalam Bahasa Indonesia
NAMA_BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}

# Nama hari dalam Bahasa Indonesia (Python weekday(): 0=Senin, 6=Minggu)
NAMA_HARI = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu",
}


class DimDate(db.Model):
    """Dimensi tanggal — atribut waktu dari setiap tanggal unik transaksi."""
    __tablename__ = "dwh_dim_date"

    # date_id berformat "YYYYMMDD", misal "20260531"
    date_id     = db.Column(db.String(8), primary_key=True)
    full_date   = db.Column(db.Date, nullable=False)
    day         = db.Column(db.Integer)
    month       = db.Column(db.Integer)
    month_name  = db.Column(db.String(20))   # misal "Mei"
    quarter     = db.Column(db.Integer)
    year        = db.Column(db.Integer)
    day_of_week = db.Column(db.String(10))   # misal "Sabtu"
    is_weekend  = db.Column(db.Boolean)

    def __repr__(self):
        return f"<DimDate {self.date_id}>"


class DimUser(db.Model):
    """Dimensi pengguna — salinan ringkas dari tabel users OLTP."""
    __tablename__ = "dwh_dim_user"

    user_id    = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    email      = db.Column(db.String(200))
    created_at = db.Column(db.Date)

    def __repr__(self):
        return f"<DimUser {self.email}>"


class DimWallet(db.Model):
    """Dimensi dompet — salinan ringkas dari tabel wallets OLTP."""
    __tablename__ = "dwh_dim_wallet"

    wallet_id = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100))
    type      = db.Column(db.String(50))

    def __repr__(self):
        return f"<DimWallet {self.name}>"


class DimCategory(db.Model):
    """Dimensi kategori — salinan ringkas dari tabel categories OLTP."""
    __tablename__ = "dwh_dim_category"

    category_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100))
    kind        = db.Column(db.String(10))   # "income" atau "expense"

    def __repr__(self):
        return f"<DimCategory {self.name}>"


class FactTransaction(db.Model):
    """
    Tabel fakta — satu baris per transaksi OLTP yang sudah di-ETL.
    fact_id = transaction.id dari OLTP sehingga ETL idempoten (tidak duplikasi baris).
    """
    __tablename__ = "dwh_fact_transaction"

    # Tidak autoincrement — nilai diambil dari transaction.id OLTP
    fact_id          = db.Column(db.Integer, primary_key=True, autoincrement=False)
    date_id          = db.Column(db.String(8),  db.ForeignKey("dwh_dim_date.date_id"))
    user_id          = db.Column(db.Integer,    db.ForeignKey("dwh_dim_user.user_id"))
    wallet_id        = db.Column(db.Integer,    db.ForeignKey("dwh_dim_wallet.wallet_id"))
    category_id      = db.Column(db.Integer,    db.ForeignKey("dwh_dim_category.category_id"),
                                 nullable=True)
    amount           = db.Column(db.Numeric(15, 2))
    kind             = db.Column(db.String(10))           # "income" atau "expense"
    usd_rate_at_date = db.Column(db.Float, nullable=True)
    erosi_persen     = db.Column(db.Float, nullable=True)
    etl_loaded_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FactTransaction {self.fact_id} {self.kind} {self.amount}>"
