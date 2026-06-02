from app.extensions import db


class SavingsGoal(db.Model):
    """Target tabungan pengguna."""
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    target_amount = db.Column(db.Integer, nullable=False)   # target dalam rupiah
    saved_amount = db.Column(db.Integer, default=0)         # jumlah yang sudah terkumpul
    deadline = db.Column(db.Date, nullable=True)            # tenggat waktu opsional

    def __repr__(self):
        return f"<SavingsGoal {self.name}>"
