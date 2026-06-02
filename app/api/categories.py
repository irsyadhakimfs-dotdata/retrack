from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.category import Category

bp = Blueprint("categories", __name__, url_prefix="/api/categories")


def _cat_json(cat):
    return {"id": cat.id, "name": cat.name, "kind": cat.kind, "icon": cat.icon}


@bp.route("", methods=["GET"])
@login_required
def list_categories():
    kind = request.args.get("kind")
    q = Category.query.filter_by(user_id=current_user.id)
    if kind in ("income", "expense"):
        q = q.filter_by(kind=kind)
    return jsonify({"ok": True, "data": [_cat_json(c) for c in q.all()]})


@bp.route("", methods=["POST"])
@login_required
def create_category():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    kind = data.get("kind")

    if not name:
        return jsonify({"ok": False, "error": "name wajib diisi"}), 400
    if kind not in ("income", "expense"):
        return jsonify({"ok": False, "error": "kind harus income atau expense"}), 400

    cat = Category(user_id=current_user.id, name=name, kind=kind,
                   icon=data.get("icon"))
    db.session.add(cat)
    db.session.commit()
    return jsonify({"ok": True, "data": _cat_json(cat)}), 201


@bp.route("/<int:cat_id>", methods=["PUT"])
@login_required
def update_category(cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    if "name" in data:
        cat.name = (data["name"] or "").strip() or cat.name
    if "kind" in data:
        if data["kind"] not in ("income", "expense"):
            return jsonify({"ok": False, "error": "kind tidak valid"}), 400
        cat.kind = data["kind"]
    if "icon" in data:
        cat.icon = data["icon"]

    db.session.commit()
    return jsonify({"ok": True, "data": _cat_json(cat)})


@bp.route("/<int:cat_id>", methods=["DELETE"])
@login_required
def delete_category(cat_id):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Kategori berhasil dihapus"}})
