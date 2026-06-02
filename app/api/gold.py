# Blueprint API investasi emas — CRUD kepemilikan emas + ringkasan nilai.
# Ledger terpisah: TIDAK mengubah saldo dompet. Selalu mengembalikan JSON {ok, data}.

from datetime import date as date_type, datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.extensions import db
from app.models.gold_holding import GoldHolding

bp = Blueprint("gold", __name__, url_prefix="/api/gold")


def _harga_emas_per_gram_sekarang():
    """Harga emas terkini (Rupiah per gram) dari market_service. None bila gagal."""
    try:
        from app.services.market_service import get_gold_per_gram
        return get_gold_per_gram().get("price_idr")
    except Exception:
        return None


def _holding_json(h, harga_now=None):
    """Serialisasi satu kepemilikan emas + hitung nilai sekarang & kenaikan bila harga ada."""
    biaya = h.grams * h.buy_price_per_gram  # total modal beli
    data = {
        "id": h.id,
        "grams": h.grams,
        "buy_price_per_gram": h.buy_price_per_gram,
        # Tanggal & waktu masuk (pembelian) — "date" tetap YYYY-MM-DD, "time" = HH:MM
        "buy_date": h.buy_date.date().isoformat(),
        "buy_time": h.buy_date.strftime("%H:%M"),
        "buy_datetime": h.buy_date.isoformat(),
        "note": h.note,
        "cost": round(biaya),
        # Field nilai sekarang (diisi bila harga pasar tersedia)
        "current_price_per_gram": None,
        "current_value": None,
        "gain": None,
        "gain_persen": None,
    }

    if harga_now:
        nilai_sekarang = h.grams * harga_now
        kenaikan = nilai_sekarang - biaya
        data["current_price_per_gram"] = round(harga_now)
        data["current_value"] = round(nilai_sekarang)
        data["gain"] = round(kenaikan)
        data["gain_persen"] = round(kenaikan / biaya * 100, 2) if biaya else None

    return data


def _parse_buy_datetime(data):
    """Bangun objek datetime dari field 'date' (wajib) + 'time' (opsional). (dt, error)."""
    try:
        tgl = date_type.fromisoformat(data["date"])
    except (ValueError, KeyError, TypeError):
        return None, "Format tanggal harus YYYY-MM-DD"

    jam = data.get("time")
    if jam:
        try:
            jam_obj = datetime.strptime(jam, "%H:%M").time()
        except ValueError:
            return None, "Format waktu harus HH:MM"
        return datetime.combine(tgl, jam_obj), None
    # Tanpa jam → pakai jam saat ini (konsisten dengan transaksi)
    return datetime.combine(tgl, datetime.now().time()), None


@bp.route("", methods=["GET"])
@login_required
def list_holdings():
    """Daftar kepemilikan emas user + ringkasan nilai & kenaikan total."""
    holdings = (
        GoldHolding.query
        .filter_by(user_id=current_user.id)
        .order_by(GoldHolding.buy_date.desc())
        .all()
    )
    harga_now = _harga_emas_per_gram_sekarang()
    items = [_holding_json(h, harga_now) for h in holdings]

    # Ringkasan total
    total_gram = sum(h.grams for h in holdings)
    total_biaya = sum(h.grams * h.buy_price_per_gram for h in holdings)
    total_nilai = sum(i["current_value"] for i in items) if harga_now else None
    total_kenaikan = (total_nilai - total_biaya) if harga_now else None
    gain_persen = (
        round(total_kenaikan / total_biaya * 100, 2)
        if (harga_now and total_biaya) else None
    )

    summary = {
        "total_grams": round(total_gram, 4),
        "total_cost": round(total_biaya),
        "total_value": round(total_nilai) if total_nilai is not None else None,
        "total_gain": round(total_kenaikan) if total_kenaikan is not None else None,
        "gain_persen": gain_persen,
        "count": len(holdings),
    }

    return jsonify({
        "ok": True,
        "data": {
            "holdings": items,
            "summary": summary,
            "current_price_per_gram": round(harga_now) if harga_now else None,
        },
    })


@bp.route("", methods=["POST"])
@login_required
def create_holding():
    """Tambah catatan pembelian emas baru."""
    data = request.get_json() or {}

    # Validasi field wajib
    required = ["grams", "buy_price_per_gram", "date"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"ok": False, "error": f"Field wajib: {', '.join(missing)}"}), 400

    try:
        grams = float(data["grams"])
        harga = int(data["buy_price_per_gram"])
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "grams dan buy_price_per_gram harus angka"}), 400

    if grams <= 0 or harga <= 0:
        return jsonify({"ok": False, "error": "grams dan harga harus lebih dari 0"}), 400

    buy_dt, err = _parse_buy_datetime(data)
    if err:
        return jsonify({"ok": False, "error": err}), 400

    h = GoldHolding(
        user_id=current_user.id,
        grams=grams,
        buy_price_per_gram=harga,
        buy_date=buy_dt,
        note=data.get("note"),
    )
    db.session.add(h)
    db.session.commit()
    return jsonify({"ok": True, "data": _holding_json(h, _harga_emas_per_gram_sekarang())}), 201


@bp.route("/<int:holding_id>", methods=["PUT"])
@login_required
def update_holding(holding_id):
    """Ubah catatan pembelian emas (termasuk waktu masuk yang bisa diedit)."""
    h = GoldHolding.query.filter_by(id=holding_id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}

    if "grams" in data:
        try:
            grams = float(data["grams"])
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "grams harus angka"}), 400
        if grams <= 0:
            return jsonify({"ok": False, "error": "grams harus lebih dari 0"}), 400
        h.grams = grams

    if "buy_price_per_gram" in data:
        try:
            harga = int(data["buy_price_per_gram"])
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "buy_price_per_gram harus angka"}), 400
        if harga <= 0:
            return jsonify({"ok": False, "error": "harga harus lebih dari 0"}), 400
        h.buy_price_per_gram = harga

    # Ubah tanggal/waktu masuk bila dikirim
    if "date" in data:
        buy_dt, err = _parse_buy_datetime(data)
        if err:
            return jsonify({"ok": False, "error": err}), 400
        h.buy_date = buy_dt
    elif "time" in data and data["time"]:
        # Hanya jam yang diubah, pertahankan tanggal
        try:
            jam_obj = datetime.strptime(data["time"], "%H:%M").time()
        except ValueError:
            return jsonify({"ok": False, "error": "Format waktu harus HH:MM"}), 400
        h.buy_date = datetime.combine(h.buy_date.date(), jam_obj)

    if "note" in data:
        h.note = data["note"]

    db.session.commit()
    return jsonify({"ok": True, "data": _holding_json(h, _harga_emas_per_gram_sekarang())})


@bp.route("/<int:holding_id>", methods=["DELETE"])
@login_required
def delete_holding(holding_id):
    """Hapus catatan pembelian emas."""
    h = GoldHolding.query.filter_by(id=holding_id, user_id=current_user.id).first_or_404()
    db.session.delete(h)
    db.session.commit()
    return jsonify({"ok": True, "data": {"message": "Catatan emas berhasil dihapus"}})
