from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.budget import Budget
from app.models.category import Category
from app.services.budget_service import hitung_budget

bp = Blueprint("budgets", __name__, url_prefix="/api/budgets")


def _budget_json(budget):
    # Ambil nama kategori dari database (gunakan db.session.get untuk SQLAlchemy 2.x)
    cat = db.session.get(Category, budget.category_id)
    nama_kategori = cat.name if cat else "?"
    icon_kategori = cat.icon if cat else None

    info = hitung_budget(budget)
    # Tambahkan field alias untuk kompatibilitas frontend
    info["persen_terpakai"] = info.pop("persen", 0)

    return {
        "id": budget.id,
        "category_id": budget.category_id,
        "nama_kategori": nama_kategori,
        "icon_kategori": icon_kategori,
        "month": budget.month,
        "year": budget.year,
        "limit_amount": budget.limit_amount,
        **info,
    }


@bp.route("", methods=["GET"])
@login_required
def list_budgets():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    q = Budget.query.filter_by(user_id=current_user.id)
    if month:
        q = q.filter_by(month=month)
    if year:
        q = q.filter_by(year=year)
    return jsonify({"ok": True, "data": [_budget_json(b) for b in q.all()]})


@bp.route("", methods=["POST"])
@login_required
def create_budget():
    data = request.get_json() or {}
    required = ["category_id", "month", "year", "limit_amount"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return jsonify({"ok": False, "error": f"Field wajib: {', '.join(missing)}"}), 400

    # Cegah duplikat (user, category, month, year)
    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=data["category_id"],
        month=data["month"],
        year=data["year"],
    ).first()
    if existing:
        return jsonify({"ok": False, "error": "Budget untuk kategori & bulan ini sudah ada"}), 409

    budget = Budget(
        user_id=current_user.id,
        category_id=data["category_id"],
        month=int(data["month"]),
        year=int(data["year"]),
        limit_amount=int(data["limit_amount"]),
    )
    db.session.add(budget)
    db.session.commit()
    return jsonify({"ok": True, "data": _budget_json(budget)}), 201


@bp.route("/<int:budget_id>", methods=["PUT"])
@login_required
def update_budget(budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    if "limit_amount" in data:
        budget.limit_amount = int(data["limit_amount"])
    db.session.commit()
    return jsonify({"ok": True, "data": _budget_json(budget)})


@bp.route("/<int:budget_id>", methods=["DELETE"])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Budget berhasil dihapus"}})
