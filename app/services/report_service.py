from datetime import datetime, time, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category


def get_summary(user_id, month, year):
    """Ringkasan total income, expense, dan selisih untuk bulan tertentu."""
    def _sum(kind):
        return db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.kind == kind,
            db.extract("month", Transaction.date) == month,
            db.extract("year", Transaction.date) == year,
        ).scalar() or 0

    income = _sum("income")
    expense = _sum("expense")
    return {"income": income, "expense": expense, "selisih": income - expense,
            "month": month, "year": year}


def get_by_category(user_id, month, year):
    """Total pengeluaran per kategori untuk bulan tertentu."""
    rows = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label("total"),
    ).filter(
        Transaction.user_id == user_id,
        Transaction.kind == "expense",
        db.extract("month", Transaction.date) == month,
        db.extract("year", Transaction.date) == year,
    ).group_by(Transaction.category_id).all()

    result = []
    for row in rows:
        cat = db.session.get(Category, row.category_id)
        result.append({
            "category_id": row.category_id,
            "category_name": cat.name if cat else "?",
            "total": row.total,
        })
    return sorted(result, key=lambda x: x["total"], reverse=True)


def _batas_rentang(start_date, end_date):
    """Ubah [start_date, end_date] (date) → batas datetime [awal, akhir) inklusif harian."""
    awal = datetime.combine(start_date, time.min)
    akhir = datetime.combine(end_date + timedelta(days=1), time.min)
    return awal, akhir


def get_summary_range(user_id, start_date, end_date):
    """Ringkasan income/expense/selisih untuk rentang tanggal [start, end] (inklusif).

    Dipakai mode 'N hari terakhir' (mis. 30 hari) — tidak terikat bulan kalender.
    """
    awal, akhir = _batas_rentang(start_date, end_date)

    def _sum(kind):
        return db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.kind == kind,
            Transaction.date >= awal,
            Transaction.date < akhir,
        ).scalar() or 0

    income = _sum("income")
    expense = _sum("expense")
    return {"income": income, "expense": expense, "selisih": income - expense,
            "start": start_date.isoformat(), "end": end_date.isoformat()}


def get_by_category_range(user_id, start_date, end_date):
    """Total pengeluaran per kategori untuk rentang tanggal [start, end] (inklusif)."""
    awal, akhir = _batas_rentang(start_date, end_date)
    rows = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label("total"),
    ).filter(
        Transaction.user_id == user_id,
        Transaction.kind == "expense",
        Transaction.date >= awal,
        Transaction.date < akhir,
    ).group_by(Transaction.category_id).all()

    result = []
    for row in rows:
        cat = db.session.get(Category, row.category_id)
        result.append({
            "category_id": row.category_id,
            "category_name": cat.name if cat else "?",
            "total": row.total,
        })
    return sorted(result, key=lambda x: x["total"], reverse=True)


def get_trend(user_id, months=6):
    """
    Tren income & expense untuk N bulan terakhir.
    Mengembalikan list dari bulan terlama ke terbaru.
    """
    from datetime import date
    today = date.today()

    hasil = []
    for i in range(months - 1, -1, -1):
        # Hitung bulan mundur dari sekarang
        total_months = today.month - 1 - i
        year = today.year + total_months // 12
        month = total_months % 12 + 1
        # Koreksi bila hasil negatif
        if total_months < 0:
            year = today.year - 1 + (total_months + 12) // 12
            month = (today.month - 1 - i) % 12 + 1

        summary = get_summary(user_id, month, year)
        hasil.append({"month": month, "year": year,
                      "income": summary["income"], "expense": summary["expense"]})
    return hasil


def get_trend_daily(user_id, start_date, end_date):
    """
    Tren income & expense PER HARI untuk rentang [start_date, end_date] (inklusif).
    Setiap hari dalam rentang selalu muncul (hari tanpa transaksi diisi 0),
    diurutkan dari tanggal terlama ke terbaru.
    Mengembalikan list dict: {"date": "YYYY-MM-DD", "income": int, "expense": int}.
    """
    # Batas waktu: dari 00:00:00 hari awal sampai sebelum 00:00 hari setelah akhir
    awal = datetime.combine(start_date, time.min)
    akhir = datetime.combine(end_date + timedelta(days=1), time.min)

    # Agregasi sekali jalan: kelompokkan per (tanggal, jenis)
    rows = db.session.query(
        func.date(Transaction.date).label("d"),
        Transaction.kind,
        func.sum(Transaction.amount),
    ).filter(
        Transaction.user_id == user_id,
        Transaction.date >= awal,
        Transaction.date < akhir,
    ).group_by("d", Transaction.kind).all()

    # Peta tanggal -> {income, expense}
    bucket = {}
    for d, kind, total in rows:
        # func.date() mengembalikan string "YYYY-MM-DD" di SQLite
        ds = d if isinstance(d, str) else d.isoformat()
        bucket.setdefault(ds, {"income": 0, "expense": 0})
        if kind in ("income", "expense"):
            bucket[ds][kind] = int(total or 0)

    # Bangun deret harian lengkap (isi 0 untuk hari kosong)
    hasil = []
    kursor = start_date
    while kursor <= end_date:
        ds = kursor.isoformat()
        b = bucket.get(ds, {"income": 0, "expense": 0})
        hasil.append({"date": ds, "income": b["income"], "expense": b["expense"]})
        kursor += timedelta(days=1)
    return hasil
