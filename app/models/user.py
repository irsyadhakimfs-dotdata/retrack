from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Model pengguna aplikasi ReFinance."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relasi ke tabel lain (cascade delete bila user dihapus)
    wallets = db.relationship("Wallet", backref="owner", lazy=True, cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="owner", lazy=True, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="owner", lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship("Budget", backref="owner", lazy=True, cascade="all, delete-orphan")
    goals = db.relationship("SavingsGoal", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash dan simpan password pengguna."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifikasi password terhadap hash yang tersimpan."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
