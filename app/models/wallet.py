from app.extensions import db

# Tipe wallet yang diizinkan
WALLET_TYPES = ("cash", "bank", "ewallet")


class Wallet(db.Model):
    """Rekening / dompet milik pengguna."""
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(20), nullable=False, default="cash")
    # Saldo awal saat wallet dibuat; saldo berjalan dihitung di service
    initial_balance = db.Column(db.Integer, default=0)

    transactions = db.relationship("Transaction", backref="wallet", lazy=True)

    def __repr__(self):
        return f"<Wallet {self.name}>"
