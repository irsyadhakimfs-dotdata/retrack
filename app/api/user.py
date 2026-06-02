"""
Blueprint user — endpoint profil pengguna dan ganti password.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db

bp = Blueprint("user", __name__, url_prefix="/api/auth")


@bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """Kembalikan data profil pengguna yang sedang login."""
    return jsonify({
        "ok": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    })


@bp.route("/me", methods=["PUT"])
@login_required
def update_me():
    """Perbarui nama pengguna yang sedang login."""
    data = request.get_json() or {}
    nama_baru = (data.get("name") or "").strip()

    if not nama_baru:
        return jsonify({"ok": False, "error": "Nama tidak boleh kosong"}), 400

    current_user.name = nama_baru
    db.session.commit()

    return jsonify({
        "ok": True,
        "data": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    })


@bp.route("/password", methods=["PUT"])
@login_required
def change_password():
    """Ganti password pengguna yang sedang login."""
    data = request.get_json() or {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    # Validasi field
    if not current_password or not new_password:
        return jsonify({"ok": False, "error": "current_password dan new_password wajib diisi"}), 400

    # Periksa password lama
    if not current_user.check_password(current_password):
        return jsonify({"ok": False, "error": "Kata sandi lama tidak sesuai"}), 400

    # Minimal 8 karakter untuk password baru
    if len(new_password) < 8:
        return jsonify({"ok": False, "error": "Kata sandi baru minimal 8 karakter"}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"ok": True, "data": {"message": "Kata sandi berhasil diubah"}})
