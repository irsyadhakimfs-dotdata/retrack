from app.extensions import db


class Budget(db.Model):
    """Batas anggaran per kategori per bulan."""
    __tablename__ = "budgets"

    # Setiap kombinasi (user, kategori, bulan, tahun) harus unik
    __table_args__ = (
        db.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_budget_user_cat_month"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    month = db.Column(db.Integer, nullable=False)       # 1–12
    year = db.Column(db.Integer, nullable=False)
    limit_amount = db.Column(db.Integer, nullable=False)  # dalam rupiah

    def __repr__(self):
        return f"<Budget {self.category_id} {self.month}/{self.year}>"
