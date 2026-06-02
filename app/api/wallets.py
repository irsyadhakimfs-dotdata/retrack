from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.wallet import Wallet
from app.models.transaction import Transaction

bp = Blueprint("wallets", __name__, url_prefix="/api/wallets")


def _hitung_saldo(wallet):
    """Saldo berjalan = initial_balance + income − expense."""
    from sqlalchemy import func
    income = db.session.query(func.sum(Transaction.amount)).filter_by(
        wallet_id=wallet.id, kind="income").scalar() or 0
    expense = db.session.query(func.sum(Transaction.amount)).filter_by(
        wallet_id=wallet.id, kind="expense").scalar() or 0
    return wallet.initial_balance + income - expense


def _wallet_json(wallet):
    return {
        "id": wallet.id,
        "name": wallet.name,
        "type": wallet.type,
        "initial_balance": wallet.initial_balance,
        "saldo": _hitung_saldo(wallet),
    }


@bp.route("", methods=["GET"])
@login_required
def list_wallets():
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()
    return jsonify({"ok": True, "data": [_wallet_json(w) for w in wallets]})


@bp.route("", methods=["POST"])
@login_required
def create_wallet():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    type_ = data.get("type", "cash")
    initial_balance = data.get("initial_balance", 0)

    if not name:
        return jsonify({"ok": False, "error": "name wajib diisi"}), 400
    if type_ not in ("cash", "bank", "ewallet"):
        return jsonify({"ok": False, "error": "type harus cash/bank/ewallet"}), 400

    wallet = Wallet(user_id=current_user.id, name=name, type=type_,
                    initial_balance=int(initial_balance))
    db.session.add(wallet)
    db.session.commit()
    return jsonify({"ok": True, "data": _wallet_json(wallet)}), 201


@bp.route("/<int:wallet_id>", methods=["PUT"])
@login_required
def update_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    if "name" in data:
        wallet.name = (data["name"] or "").strip() or wallet.name
    if "type" in data:
        if data["type"] not in ("cash", "bank", "ewallet"):
            return jsonify({"ok": False, "error": "type tidak valid"}), 400
        wallet.type = data["type"]
    if "initial_balance" in data:
        wallet.initial_balance = int(data["initial_balance"])

    db.session.commit()
    return jsonify({"ok": True, "data": _wallet_json(wallet)})


@bp.route("/<int:wallet_id>", methods=["DELETE"])
@login_required
def delete_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id, user_id=current_user.id).first_or_404()

    # Tolak penghapusan jika masih ada transaksi terkait
    if Transaction.query.filter_by(wallet_id=wallet.id).count() > 0:
        return jsonify({"ok": False, "error": "Wallet masih memiliki transaksi, tidak bisa dihapus"}), 409

    db.session.delete(wallet)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Wallet berhasil dihapus"}})
