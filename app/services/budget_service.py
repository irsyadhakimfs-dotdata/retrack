from sqlalchemy import func
from app.extensions import db
from app.models.transaction import Transaction


def hitung_budget(budget):
    """
    Hitung pemakaian, sisa, dan status sebuah budget.
    Status: 'aman' (<80%), 'hampir' (>=80%), 'lewat' (>100%).
    """
    terpakai = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == budget.user_id,
        Transaction.category_id == budget.category_id,
        Transaction.kind == "expense",
        db.extract("month", Transaction.date) == budget.month,
        db.extract("year", Transaction.date) == budget.year,
    ).scalar() or 0

    sisa = budget.limit_amount - terpakai

    if budget.limit_amount == 0:
        persen = 0.0
    else:
        persen = terpakai / budget.limit_amount * 100

    if persen > 100:
        status = "lewat"
    elif persen >= 80:
        status = "hampir"
    else:
        status = "aman"

    return {
        "terpakai": terpakai,
        "sisa": sisa,
        "persen": round(persen, 2),
        "status": status,
    }
