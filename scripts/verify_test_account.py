"""
Cetak ringkasan akun test: jumlah dompet/kategori/transaksi, rentang tanggal,
dan saldo akhir tiap dompet (+ tanda bila ada yang negatif).

Pakai (dev):  python scripts/verify_test_account.py
Pakai (prod): set FLASK_ENV=production & DATABASE_URL lalu jalankan.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction
from app.api.wallets import _hitung_saldo

EMAIL = "test@retrack.app"


def main():
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        u = User.query.filter_by(email=EMAIL).first()
        if not u:
            print(f"[GAGAL] user {EMAIL} tidak ada")
            return 1
        nw = Wallet.query.filter_by(user_id=u.id).count()
        nc = Category.query.filter_by(user_id=u.id).count()
        trx = Transaction.query.filter_by(user_id=u.id).all()
        dates = [t.date for t in trx]
        dmin = min(dates).date() if dates else None
        dmax = max(dates).date() if dates else None
        print(f"User    : {u.name} <{u.email}> id={u.id}")
        print(f"Dompet  : {nw} | Kategori: {nc} | Transaksi: {len(trx)}")
        print(f"Rentang : {dmin} .. {dmax}")
        ok = True
        for w in Wallet.query.filter_by(user_id=u.id):
            s = _hitung_saldo(w)
            if s < 0:
                ok = False
            print(f"  - {w.name} ({w.type}): saldo {s:,}"
                  f"{'  <-- NEGATIF!' if s < 0 else ''}")
        print("Saldo   :", "OK (semua >= 0)" if ok else "ADA NEGATIF")
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
