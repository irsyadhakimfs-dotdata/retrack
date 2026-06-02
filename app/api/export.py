"""
Blueprint export — endpoint untuk mengunduh data sebagai CSV.
"""

import csv
import io
from flask import Blueprint, Response
from flask_login import login_required, current_user
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.wallet import Wallet

bp = Blueprint("export", __name__, url_prefix="/api/export")


@bp.route("/csv")
@login_required
def export_csv():
    """
    Unduh semua transaksi milik pengguna saat ini dalam format CSV.
    Kolom: tanggal, jenis, kategori, wallet, nominal, catatan, kurs_usd
    """
    # Ambil semua transaksi user, urut dari yang terbaru
    transaksi_list = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )

    # Buat buffer string untuk CSV
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    # Tulis baris header
    writer.writerow([
        "Tanggal",
        "Jenis",
        "Kategori",
        "Dompet",
        "Nominal (Rp)",
        "Catatan",
        "Kurs USD saat transaksi",
    ])

    # Import db di sini untuk menghindari circular import
    from app.extensions import db

    # Tulis setiap baris transaksi
    for trx in transaksi_list:
        # Ambil nama kategori (bisa None jika kategori dihapus) — gunakan db.session.get untuk SQLAlchemy 2.x
        kategori = db.session.get(Category, trx.category_id)
        nama_kategori = kategori.name if kategori else "(tanpa kategori)"

        # Ambil nama wallet
        wallet = db.session.get(Wallet, trx.wallet_id)
        nama_wallet = wallet.name if wallet else "(tanpa dompet)"

        # Tipe transaksi dalam Bahasa Indonesia
        jenis = "Pemasukan" if trx.kind == "income" else "Pengeluaran"

        # Kurs USD saat transaksi (hanya ada untuk income)
        kurs_usd = trx.usd_rate_at_date if trx.usd_rate_at_date else ""

        writer.writerow([
            trx.date.strftime("%Y-%m-%d"),
            jenis,
            nama_kategori,
            nama_wallet,
            trx.amount,
            trx.note or "",
            kurs_usd,
        ])

    # Pindah ke awal buffer
    output.seek(0)

    # Kembalikan sebagai file CSV yang bisa diunduh
    return Response(
        output.getvalue().encode("utf-8-sig"),  # utf-8-sig agar Excel baca BOM
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=refinance-export.csv",
            "Content-Type": "text/csv; charset=utf-8",
        },
    )
