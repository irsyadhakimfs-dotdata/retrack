from datetime import datetime, timezone
from app.extensions import db


class GoldHolding(db.Model):
    """
    Catatan kepemilikan investasi emas (ledger terpisah, tidak menyentuh saldo dompet).

    Tujuan: mencatat berapa gram emas yang dimiliki, KAPAN dibeli (bisa diedit),
    dan harga belinya per gram — agar aplikasi bisa menghitung kenaikan nilai
    terhadap harga emas terkini.
    """
    __tablename__ = "gold_holdings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Berat emas dalam gram
    grams = db.Column(db.Float, nullable=False)

    # Harga beli per gram dalam Rupiah (untuk menghitung kenaikan/keuntungan)
    buy_price_per_gram = db.Column(db.Integer, nullable=False)

    # Waktu/tanggal masuk (pembelian). Bisa diedit oleh pengguna agar bisa dikoreksi.
    buy_date = db.Column(db.DateTime, nullable=False)

    # Catatan opsional (mis. "Antam 5gr", "Pegadaian")
    note = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<GoldHolding {self.grams}gr @ {self.buy_price_per_gram}/gr>"
