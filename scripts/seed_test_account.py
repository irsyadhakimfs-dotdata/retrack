"""
Buat (idempoten) akun test + semua dompet & kategori yang dipakai dataset Andi.

Dipakai sebelum import CSV: import_keuangan_csv.py mencocokkan Kategori/Dompet
ke baris yang HARUS sudah ada. Aman dijalankan berulang.

Pakai:
    python scripts/seed_test_account.py
"""
import os
import sys

# Root proyek (untuk import app) + folder scripts (untuk import generator)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from generate_andi_dataset import (
    WALLETS, CATEGORIES, TEST_EMAIL, TEST_NAME, TEST_PASSWORD,
)


def seed_test_account():
    """Pastikan user test + dompet + kategori ada. Kembalikan objek user."""
    user = User.query.filter_by(email=TEST_EMAIL).first()
    if not user:
        user = User(email=TEST_EMAIL, name=TEST_NAME)
        user.set_password(TEST_PASSWORD)
        db.session.add(user)
        db.session.flush()  # agar user.id terisi
    else:
        # Selaraskan nama & password bila akun sudah ada
        user.name = TEST_NAME
        user.set_password(TEST_PASSWORD)

    punya_wal = {w.name.strip().lower()
                 for w in Wallet.query.filter_by(user_id=user.id)}
    for name, type_, init in WALLETS:
        if name.strip().lower() not in punya_wal:
            db.session.add(Wallet(user_id=user.id, name=name,
                                  type=type_, initial_balance=init))

    punya_kat = {c.name.strip().lower()
                 for c in Category.query.filter_by(user_id=user.id)}
    for name, kind in CATEGORIES:
        if name.strip().lower() not in punya_kat:
            db.session.add(Category(user_id=user.id, name=name, kind=kind))

    db.session.commit()
    return user


def main():
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        user = seed_test_account()
        nw = Wallet.query.filter_by(user_id=user.id).count()
        nc = Category.query.filter_by(user_id=user.id).count()
        print(f"[SUKSES] Akun test siap: {user.name} <{user.email}> "
              f"(id={user.id}) - {nw} dompet, {nc} kategori.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
