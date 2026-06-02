from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/register", methods=["POST"])
def register():
    """Daftarkan pengguna baru."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return jsonify({"ok": False, "error": "email, password, dan name wajib diisi"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"ok": False, "error": "Email sudah terdaftar"}), 409

    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"ok": True, "data": {"id": user.id, "email": user.email, "name": user.name}}), 201


@bp.route("/login", methods=["POST"])
def login():
    """Login pengguna yang sudah terdaftar."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"ok": False, "error": "Email atau password salah"}), 401

    login_user(user)
    return jsonify({"ok": True, "data": {"id": user.id, "email": user.email, "name": user.name}})


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout pengguna yang sedang login."""
    logout_user()
    return jsonify({"ok": True, "data": {"message": "Berhasil logout"}})
