from app.extensions import db

# Jenis kategori yang diizinkan
CATEGORY_KINDS = ("income", "expense")


class Category(db.Model):
    """Kategori pemasukan atau pengeluaran."""
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(60), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # "income" atau "expense"
    icon = db.Column(db.String(50), nullable=True)   # nama ikon opsional

    transactions = db.relationship("Transaction", backref="category", lazy=True)
    budgets = db.relationship("Budget", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name} ({self.kind})>"
