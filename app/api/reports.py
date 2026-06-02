from datetime import date, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services import report_service

# Nama bulan singkat (Bahasa Indonesia) untuk label grafik
NAMA_BULAN_SINGKAT = [
    "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agt", "Sep", "Okt", "Nov", "Des",
]

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _bulan_tahun_sekarang():
    today = date.today()
    return today.month, today.year


# Batas maksimal rentang "N hari terakhir" (~6 bulan) agar grafik & query tetap wajar
MAX_RANGE_DAYS = 186


def _rentang_hari(days):
    """Kembalikan (start_date, end_date) untuk N hari terakhir (inklusif hari ini)."""
    n = max(1, min(days, MAX_RANGE_DAYS))
    end = date.today()
    start = end - timedelta(days=n - 1)
    return start, end


@bp.route("/summary")
@login_required
def summary():
    # Mode baru: ?days=N → ringkasan N hari terakhir (tidak terikat bulan).
    # Mode lama: ?month=&year= tetap didukung (kompatibel test & fitur lain).
    days = request.args.get("days", type=int)
    if days:
        start, end = _rentang_hari(days)
        data = report_service.get_summary_range(current_user.id, start, end)
        return jsonify({"ok": True, "data": data})

    today = date.today()
    month = request.args.get("month", today.month, type=int)
    year = request.args.get("year", today.year, type=int)
    data = report_service.get_summary(current_user.id, month, year)
    return jsonify({"ok": True, "data": data})


@bp.route("/by-category")
@login_required
def by_category():
    days = request.args.get("days", type=int)
    if days:
        start, end = _rentang_hari(days)
        data = report_service.get_by_category_range(current_user.id, start, end)
        return jsonify({"ok": True, "data": data})

    today = date.today()
    month = request.args.get("month", today.month, type=int)
    year = request.args.get("year", today.year, type=int)
    data = report_service.get_by_category(current_user.id, month, year)
    return jsonify({"ok": True, "data": data})


@bp.route("/trend")
@login_required
def trend():
    # Default dari konfigurasi server (TREND_DEFAULT_MONTHS); bisa di-override via ?months=N
    default_months = current_app.config.get("TREND_DEFAULT_MONTHS", 2)
    months = request.args.get("months", default_months, type=int)
    rows = report_service.get_trend(current_user.id, months)

    # Nama bulan dalam Bahasa Indonesia untuk label grafik Chart.js
    nama_bulan = [
        "", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agt", "Sep", "Okt", "Nov", "Des"
    ]

    # Konversi ke format yang mudah digunakan Chart.js — tambahkan field "label" di tiap item
    # Agar len(data) == months tetap konsisten (kompatibel dengan test lama)
    for r in rows:
        r["label"] = f"{nama_bulan[r['month']]} {str(r['year'])[2:]}"

    # Sertakan juga array terpisah sebagai "chart" untuk kemudahan frontend
    chart = {
        "labels": [r["label"] for r in rows],
        "income": [r["income"] for r in rows],
        "expense": [r["expense"] for r in rows],
    }

    # data adalah list (agar len(data) == months), chart adalah ringkasan array
    return jsonify({"ok": True, "data": rows, "chart": chart})


@bp.route("/trend-daily")
@login_required
def trend_daily():
    """
    Tren income & expense PER HARI.

    Dua mode pemakaian:
      - ?month=M&year=Y  → seluruh hari pada bulan tersebut.
      - ?days=N          → N hari terakhir (mundur dari hari ini).
    Jika keduanya kosong → default 30 hari terakhir.
    Rentang dibatasi maksimal ~6 bulan (186 hari) untuk pilihan 30 hari / 3 bulan / 6 bulan.
    """
    today = date.today()
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    days = request.args.get("days", type=int)

    if month and year:
        # Hari pertama bulan tsb. s/d hari terakhir bulan tsb.
        start = date(year, month, 1)
        if month == 12:
            bulan_depan = date(year + 1, 1, 1)
        else:
            bulan_depan = date(year, month + 1, 1)
        end = bulan_depan - timedelta(days=1)
    else:
        # Mode N hari terakhir (default 30), dibatasi 1..186 hari (~6 bulan)
        n = days if days else 30
        n = max(1, min(n, MAX_RANGE_DAYS))
        end = today
        start = today - timedelta(days=n - 1)

    rows = report_service.get_trend_daily(current_user.id, start, end)

    # Label ringkas "D Mon", mis. "30 Mei"
    for r in rows:
        d = date.fromisoformat(r["date"])
        r["label"] = f"{d.day} {NAMA_BULAN_SINGKAT[d.month]}"

    chart = {
        "labels": [r["label"] for r in rows],
        "income": [r["income"] for r in rows],
        "expense": [r["expense"] for r in rows],
    }
    return jsonify({"ok": True, "data": rows, "chart": chart})
