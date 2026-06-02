# Blueprint API DWH — endpoint untuk menjalankan ETL dan query Data Warehouse
# Semua endpoint wajib login dan selalu mengembalikan JSON {ok, data}.

from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.dwh import FactTransaction, DimDate, DimCategory
from app.services.etl_service import run_etl

bp = Blueprint("dwh", __name__, url_prefix="/api/dwh")


@bp.route("/etl/run", methods=["POST"])
@login_required
def etl_run():
    """Jalankan ETL untuk current_user, kembalikan statistik loaded/skipped/errors."""
    try:
        stats = run_etl(user_id=current_user.id)
        return jsonify({"ok": True, "data": stats})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.route("/summary")
@login_required
def summary():
    """
    Total income & expense per bulan untuk tahun tertentu (dari FactTransaction DWH).
    Query param: year (int, default tahun berjalan).
    """
    tahun = request.args.get("year", type=int, default=date.today().year)

    rows = (
        db.session.query(
            DimDate.month,
            DimDate.month_name,
            FactTransaction.kind,
            func.sum(FactTransaction.amount).label("total"),
        )
        .join(DimDate, FactTransaction.date_id == DimDate.date_id)
        .filter(FactTransaction.user_id == current_user.id)
        .filter(DimDate.year == tahun)
        .group_by(DimDate.month, DimDate.month_name, FactTransaction.kind)
        .order_by(DimDate.month)
        .all()
    )

    # Gabungkan income dan expense ke satu dict per bulan
    bulan_map = {}
    for month, month_name, kind, total in rows:
        if month not in bulan_map:
            bulan_map[month] = {
                "month": month,
                "month_name": month_name,
                "income": 0,
                "expense": 0,
            }
        bulan_map[month][kind] = float(total or 0)

    data = sorted(bulan_map.values(), key=lambda x: x["month"])
    return jsonify({"ok": True, "data": data})


@bp.route("/top-categories")
@login_required
def top_categories():
    """
    Top 5 kategori (income atau expense) N bulan terakhir (dari FactTransaction DWH).
    Query param: months (int, default 3), kind ("expense" atau "income", default "expense").
    """
    months = request.args.get("months", type=int, default=3)
    kind   = request.args.get("kind", default="expense")

    # Hitung tanggal cutoff secara tepat (mundur N bulan dari hari ini)
    today = date.today()
    cutoff_month = today.month - months
    cutoff_year  = today.year
    while cutoff_month < 1:
        cutoff_month += 12
        cutoff_year  -= 1
    # Gunakan tanggal 1 bulan tersebut sebagai batas bawah
    cutoff = date(cutoff_year, cutoff_month, 1)
    cutoff_id = cutoff.strftime("%Y%m%d")

    rows = (
        db.session.query(
            DimCategory.name,
            func.sum(FactTransaction.amount).label("total"),
            func.count(FactTransaction.fact_id).label("count"),
        )
        .join(DimCategory, FactTransaction.category_id == DimCategory.category_id)
        .filter(FactTransaction.user_id == current_user.id)
        .filter(FactTransaction.kind == kind)
        .filter(FactTransaction.date_id >= cutoff_id)
        .group_by(DimCategory.name)
        .order_by(func.sum(FactTransaction.amount).desc())
        .limit(5)
        .all()
    )

    data = [
        {"category": name, "total": float(total or 0), "count": count}
        for name, total, count in rows
    ]
    return jsonify({"ok": True, "data": data})


@bp.route("/erosi-summary")
@login_required
def erosi_summary():
    """
    Rata-rata erosi nilai dari semua transaksi income user yang punya data erosi.
    Mengembalikan avg_erosi_persen dan jumlah transaksi income.
    """
    row = (
        db.session.query(
            func.avg(FactTransaction.erosi_persen).label("avg_erosi"),
            func.count(FactTransaction.fact_id).label("total"),
        )
        .filter(FactTransaction.user_id == current_user.id)
        .filter(FactTransaction.kind == "income")
        .filter(FactTransaction.erosi_persen.isnot(None))
        .first()
    )

    avg_erosi = (
        round(float(row.avg_erosi), 4)
        if row and row.avg_erosi is not None
        else None
    )
    total = row.total if row else 0

    return jsonify({
        "ok": True,
        "data": {
            "avg_erosi_persen": avg_erosi,
            "total_income_transactions": total,
        },
    })
