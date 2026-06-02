# ETL Service — Extract, Transform, Load dari OLTP ke DWH (Star Schema)
# Logika murni bisnis; tidak ada logika tampilan di sini.

from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.dwh import (
    DimDate, DimUser, DimWallet, DimCategory, FactTransaction,
    NAMA_BULAN, NAMA_HARI,
)
from app.services.erosion_service import hitung_erosi


def _ambil_kurs_sekarang():
    """
    Ambil kurs USD/IDR terkini dari market service.
    Kembalikan float bila berhasil, None bila gagal (jaringan mati, dsb.).
    """
    try:
        from app.services.market_service import get_usd_idr
        result = get_usd_idr()
        if result and result.get("rate"):
            return float(result["rate"])
    except Exception:
        pass
    return None


def _buat_dim_date(tgl):
    """
    Bangun objek DimDate dari tanggal Python.
    Belum di-merge ke sesi; pemanggil yang melakukan merge.
    """
    weekday = tgl.weekday()          # 0=Senin … 6=Minggu
    dim = DimDate()
    dim.date_id     = tgl.strftime("%Y%m%d")
    dim.full_date   = tgl
    dim.day         = tgl.day
    dim.month       = tgl.month
    dim.month_name  = NAMA_BULAN.get(tgl.month, str(tgl.month))
    dim.quarter     = (tgl.month - 1) // 3 + 1
    dim.year        = tgl.year
    dim.day_of_week = NAMA_HARI.get(weekday, str(weekday))
    dim.is_weekend  = weekday >= 5   # Sabtu=5, Minggu=6
    return dim


def run_etl(user_id=None):
    """
    Jalankan ETL penuh: extract dari OLTP → transform → load ke DWH.
    Jika user_id diberikan, hanya proses transaksi milik user tersebut.
    Kembalikan dict {"loaded": int, "skipped": int, "errors": int}.
    ETL bersifat idempoten — menjalankan dua kali tidak menduplikasi baris.
    """
    stats = {"loaded": 0, "skipped": 0, "errors": 0}

    try:
        # --- EXTRACT: baca transaksi dari OLTP ---
        query = Transaction.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        transaksi_list = query.all()

        # Ambil kurs terkini sekali untuk seluruh batch (boleh None)
        kurs_sekarang = _ambil_kurs_sekarang()

        # --- TRANSFORM + LOAD: proses per transaksi ---
        for trx in transaksi_list:
            # Idempoten: skip bila fakta sudah ada di DWH
            if FactTransaction.query.get(trx.id) is not None:
                stats["skipped"] += 1
                continue

            try:
                # Ambil bagian tanggal saja (kolom date kini DateTime → punya komponen jam)
                tgl = trx.date.date() if isinstance(trx.date, datetime) else trx.date

                # Dimensi tanggal
                db.session.merge(_buat_dim_date(tgl))

                # Dimensi user
                user = User.query.get(trx.user_id)
                if user:
                    dim_user = DimUser()
                    dim_user.user_id    = user.id
                    dim_user.name       = user.name
                    dim_user.email      = user.email
                    # Ambil bagian date saja dari datetime created_at
                    dim_user.created_at = (
                        user.created_at.date() if user.created_at else None
                    )
                    db.session.merge(dim_user)

                # Dimensi wallet
                wallet = Wallet.query.get(trx.wallet_id)
                if wallet:
                    dim_wallet = DimWallet()
                    dim_wallet.wallet_id = wallet.id
                    dim_wallet.name      = wallet.name
                    dim_wallet.type      = wallet.type
                    db.session.merge(dim_wallet)

                # Dimensi kategori (nullable di OLTP tidak mungkin, tapi aman)
                if trx.category_id:
                    cat = Category.query.get(trx.category_id)
                    if cat:
                        dim_cat = DimCategory()
                        dim_cat.category_id = cat.id
                        dim_cat.name        = cat.name
                        dim_cat.kind        = cat.kind
                        db.session.merge(dim_cat)

                # Hitung erosi_persen bila kurs tersedia
                erosi = None
                if trx.usd_rate_at_date and kurs_sekarang:
                    hasil = hitung_erosi(trx.amount, trx.usd_rate_at_date, kurs_sekarang)
                    if hasil:
                        erosi = hasil["erosi_persen"]

                # Fakta transaksi
                fact = FactTransaction()
                fact.fact_id          = trx.id          # PK = transaction.id OLTP
                fact.date_id          = tgl.strftime("%Y%m%d")
                fact.user_id          = trx.user_id
                fact.wallet_id        = trx.wallet_id
                fact.category_id      = trx.category_id
                fact.amount           = trx.amount
                fact.kind             = trx.kind
                fact.usd_rate_at_date = trx.usd_rate_at_date
                fact.erosi_persen     = erosi
                fact.etl_loaded_at    = datetime.utcnow()
                db.session.merge(fact)

                stats["loaded"] += 1

            except Exception:
                # Catat error per transaksi tapi jangan batalkan yang lain
                stats["errors"] += 1
                db.session.rollback()

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return stats
