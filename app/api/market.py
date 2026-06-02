from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.services import market_service

bp = Blueprint("market", __name__, url_prefix="/api/market")


@bp.route("/usd-idr")
@login_required
def usd_idr():
    data = market_service.get_usd_idr()
    return jsonify({"ok": True, "data": data})


@bp.route("/gold")
@login_required
def gold():
    data = market_service.get_gold()
    return jsonify({"ok": True, "data": data})


@bp.route("/usd-idr/history")
@login_required
def usd_idr_history():
    """Riwayat kurs USD/IDR selama N bulan (default 6)."""
    try:
        months = int(request.args.get("months", 6))
        months = max(1, min(months, 24))  # batasi 1–24 bulan
    except (ValueError, TypeError):
        months = 6

    data = market_service.get_usd_idr_history(months=months)
    return jsonify({"ok": True, "data": data})


@bp.route("/gold/history")
@login_required
def gold_history():
    """Riwayat harga emas (Rupiah per gram) selama N bulan (default 6)."""
    try:
        months = int(request.args.get("months", 6))
        months = max(1, min(months, 24))  # batasi 1–24 bulan
    except (ValueError, TypeError):
        months = 6

    data = market_service.get_gold_history(months=months)
    return jsonify({"ok": True, "data": data})
