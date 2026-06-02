from datetime import datetime, timezone
from app.extensions import db


class Transaction(db.Model):
    """Transaksi keuangan (pemasukan atau pengeluaran)."""
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)          # selalu positif, dalam rupiah
    kind = db.Column(db.String(10), nullable=False)         # "income" atau "expense"
    # Tanggal + waktu transaksi. Saat dibuat lewat form, waktu = jam saat ini.
    # Untuk data lama/impor yang tidak punya jam, waktu di-set 00:00:00.
    date = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Kurs USD/IDR saat transaksi dibuat — WAJIB diisi untuk income (dasar fitur erosi)
    # Boleh null untuk expense
    usd_rate_at_date = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Transaction {self.kind} {self.amount} on {self.date}>"
