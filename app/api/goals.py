from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.savings_goal import SavingsGoal

bp = Blueprint("goals", __name__, url_prefix="/api/goals")


def _estimasi_per_bulan(goal):
    """Estimasi setoran per bulan agar goal tercapai sebelum deadline."""
    if not goal.deadline:
        return None
    sisa_target = goal.target_amount - goal.saved_amount
    if sisa_target <= 0:
        return 0
    today = date.today()
    # Hitung bulan yang tersisa (minimal 1 agar tidak dibagi nol)
    bulan_sisa = (goal.deadline.year - today.year) * 12 + (goal.deadline.month - today.month)
    if bulan_sisa <= 0:
        return sisa_target  # deadline sudah lewat, perlu lunas sekarang
    return round(sisa_target / bulan_sisa)


def _goal_json(goal):
    progress = 0.0
    if goal.target_amount > 0:
        progress = round(goal.saved_amount / goal.target_amount * 100, 2)
    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": goal.target_amount,
        "saved_amount": goal.saved_amount,
        "deadline": goal.deadline.isoformat() if goal.deadline else None,
        "progress_persen": progress,
        "estimasi_per_bulan": _estimasi_per_bulan(goal),
    }


@bp.route("", methods=["GET"])
@login_required
def list_goals():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    return jsonify({"ok": True, "data": [_goal_json(g) for g in goals]})


@bp.route("", methods=["POST"])
@login_required
def create_goal():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    target = data.get("target_amount")

    if not name or target is None:
        return jsonify({"ok": False, "error": "name dan target_amount wajib diisi"}), 400

    deadline = None
    if data.get("deadline"):
        try:
            deadline = date.fromisoformat(data["deadline"])
        except ValueError:
            return jsonify({"ok": False, "error": "Format deadline harus YYYY-MM-DD"}), 400

    goal = SavingsGoal(
        user_id=current_user.id,
        name=name,
        target_amount=int(target),
        saved_amount=int(data.get("saved_amount", 0)),
        deadline=deadline,
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({"ok": True, "data": _goal_json(goal)}), 201


@bp.route("/<int:goal_id>", methods=["PUT"])
@login_required
def update_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    if "name" in data:
        goal.name = data["name"]
    if "target_amount" in data:
        goal.target_amount = int(data["target_amount"])
    if "saved_amount" in data:
        goal.saved_amount = int(data["saved_amount"])
    if "deadline" in data:
        if data["deadline"]:
            try:
                goal.deadline = date.fromisoformat(data["deadline"])
            except ValueError:
                return jsonify({"ok": False, "error": "Format deadline harus YYYY-MM-DD"}), 400
        else:
            goal.deadline = None

    db.session.commit()
    return jsonify({"ok": True, "data": _goal_json(goal)})


@bp.route("/<int:goal_id>", methods=["DELETE"])
@login_required
def delete_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Goal berhasil dihapus"}})
