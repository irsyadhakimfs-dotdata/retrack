from datetime import date as date_type, datetime, timedelta, time
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.models.category import Category

bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


def _trx_json(trx, kurs_sekarang=None):
    """Serialisasi transaksi; sertakan objek erosi untuk income yang punya kurs."""
    data = {
        "id": trx.id,
        "wallet_id": trx.wallet_id,
        "category_id": trx.category_id,
        "amount": trx.amount,
        "kind": trx.kind,
        # "date" tetap "YYYY-MM-DD" (kompatibel kode lama); "time" = "HH:MM";
        # "datetime" = ISO lengkap untuk konsumen yang butuh keduanya.
        "date": trx.date.date().isoformat(),
        "time": trx.date.strftime("%H:%M"),
        "datetime": trx.date.isoformat(),
        "note": trx.note,
        "usd_rate_at_date": trx.usd_rate_at_date,
        "created_at": trx.created_at.isoformat(),
    }

    # Lampirkan erosi hanya untuk income yang punya kurs tersimpan
    if trx.kind == "income":
        if trx.usd_rate_at_date and kurs_sekarang:
            from app.services.erosion_service import hitung_erosi
            erosi = hitung_erosi(trx.amount, trx.usd_rate_at_date, kurs_sekarang)
            if erosi:
                # Sertakan kurs awal & sekarang agar bisa ditampilkan di tooltip frontend
                erosi["usd_rate_at_date"] = trx.usd_rate_at_date
                erosi["usd_rate_sekarang"] = kurs_sekarang
            data["erosi"] = erosi
        else:
            data["erosi"] = None  # data kurs tidak tersedia

    return data


def _kurs_sekarang():
    """Ambil kurs USD/IDR sekarang dari market_service (None bila gagal)."""
    try:
        from app.services.market_service import get_usd_idr
        result = get_usd_idr()
        return result.get("rate")
    except Exception:
        return None


def _kurs_pada_tanggal(tgl):
    """
    Ambil kurs USD/IDR pada TANGGAL transaksi (historis), bukan kurs hari ini.

    Ini fondasi fitur erosi nilai: transaksi yang dicatat mundur (backdate) harus
    memakai kurs saat transaksi benar-benar terjadi agar erosi terhitung akurat.
    Bila data historis tidak tersedia, market_service otomatis fallback ke kurs sekarang.
    Kembalikan float atau None.
    """
    try:
        from app.services.market_service import get_usd_idr_at_date
        return get_usd_idr_at_date(tgl)
    except Exception:
        return None


@bp.route("", methods=["GET"])
@login_required
def list_transactions():
    q = Transaction.query.filter_by(user_id=current_user.id)

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    days = request.args.get("days", type=int)
    category_id = request.args.get("category_id", type=int)
    keyword = request.args.get("q", "").strip()

    # Mode "N hari terakhir" (dipakai dashboard) — dibatasi 1..186 hari (~6 bulan)
    if days:
        n = max(1, min(days, 186))
        awal = datetime.combine(date_type.today() - timedelta(days=n - 1), time.min)
        q = q.filter(Transaction.date >= awal)
    if month:
        q = q.filter(db.extract("month", Transaction.date) == month)
    if year:
        q = q.filter(db.extract("year", Transaction.date) == year)
    if category_id:
        q = q.filter_by(category_id=category_id)
    if keyword:
        q = q.filter(Transaction.note.ilike(f"%{keyword}%"))

    trxs = q.order_by(Transaction.date.desc()).all()
    kurs = _kurs_sekarang()
    return jsonify({"ok": True, "data": [_trx_json(t, kurs) for t in trxs]})


@bp.route("", methods=["POST"])
@login_required
def create_transaction():
    data = request.get_json() or {}

    # Validasi field wajib
    required = ["wallet_id", "category_id", "amount", "kind", "date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"ok": False, "error": f"Field wajib: {', '.join(missing)}"}), 400

    kind = data["kind"]
    if kind not in ("income", "expense"):
        return jsonify({"ok": False, "error": "kind harus income atau expense"}), 400

    # Pastikan wallet & kategori milik user ini
    wallet = Wallet.query.filter_by(id=data["wallet_id"], user_id=current_user.id).first()
    if not wallet:
        return jsonify({"ok": False, "error": "Wallet tidak ditemukan"}), 404

    category = Category.query.filter_by(id=data["category_id"], user_id=current_user.id).first()
    if not category:
        return jsonify({"ok": False, "error": "Kategori tidak ditemukan"}), 404

    # Tanggal wajib (YYYY-MM-DD). Komponen waktu:
    #  - jika klien mengirim "time" (HH:MM) → pakai itu
    #  - jika tidak → pakai jam SAAT INI (current time) sesuai kebutuhan fitur
    try:
        tgl = date_type.fromisoformat(data["date"])
    except ValueError:
        return jsonify({"ok": False, "error": "Format tanggal harus YYYY-MM-DD"}), 400

    # Simpan kurs PADA TANGGAL transaksi untuk income (fondasi fitur erosi).
    # Memakai kurs historis agar transaksi backdate tetap akurat (bukan kurs hari ini).
    usd_rate = None
    if kind == "income":
        usd_rate = _kurs_pada_tanggal(tgl)

    jam = data.get("time")
    if jam:
        try:
            jam_obj = datetime.strptime(jam, "%H:%M").time()
        except ValueError:
            return jsonify({"ok": False, "error": "Format waktu harus HH:MM"}), 400
        trx_date = datetime.combine(tgl, jam_obj)
    else:
        # Default: tanggal yang dipilih + jam saat ini
        trx_date = datetime.combine(tgl, datetime.now().time())

    trx = Transaction(
        user_id=current_user.id,
        wallet_id=wallet.id,
        category_id=category.id,
        amount=int(data["amount"]),
        kind=kind,
        date=trx_date,
        note=data.get("note"),
        usd_rate_at_date=usd_rate,
    )
    db.session.add(trx)
    db.session.commit()
    return jsonify({"ok": True, "data": _trx_json(trx, _kurs_sekarang())}), 201


@bp.route("/<int:trx_id>", methods=["PUT"])
@login_required
def update_transaction(trx_id):
    trx = Transaction.query.filter_by(id=trx_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    if "amount" in data:
        trx.amount = int(data["amount"])
    if "note" in data:
        trx.note = data["note"]
    if "date" in data:
        try:
            tgl = date_type.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"ok": False, "error": "Format tanggal harus YYYY-MM-DD"}), 400
        # Pertahankan komponen jam yang sudah ada saat hanya tanggal yang diubah
        jam_obj = trx.date.time()
        trx.date = datetime.combine(tgl, jam_obj)
        # Tanggal berubah → perbarui kurs historis untuk income agar erosi tetap akurat
        if trx.kind == "income":
            trx.usd_rate_at_date = _kurs_pada_tanggal(tgl)

    if "time" in data and data["time"]:
        try:
            jam_obj = datetime.strptime(data["time"], "%H:%M").time()
        except ValueError:
            return jsonify({"ok": False, "error": "Format waktu harus HH:MM"}), 400
        trx.date = datetime.combine(trx.date.date(), jam_obj)
    if "category_id" in data:
        cat = Category.query.filter_by(id=data["category_id"], user_id=current_user.id).first()
        if not cat:
            return jsonify({"ok": False, "error": "Kategori tidak ditemukan"}), 404
        trx.category_id = cat.id

    db.session.commit()
    return jsonify({"ok": True, "data": _trx_json(trx, _kurs_sekarang())})


@bp.route("/<int:trx_id>", methods=["DELETE"])
@login_required
def delete_transaction(trx_id):
    trx = Transaction.query.filter_by(id=trx_id, user_id=current_user.id).first_or_404()
    db.session.delete(trx)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Transaksi berhasil dihapus"}})
