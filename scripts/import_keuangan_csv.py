"""
Skrip sekali-jalan: impor file CSV keuangan ke akun seorang user.

Cara pakai (dari root proyek):
    python scripts/import_keuangan_csv.py "keuangan_generated (1).csv" irsyadhakimfs@gmail.com

Perilaku:
  - Cari user berdasarkan email.
  - HAPUS semua transaksi lama milik user itu (+ fakta DWH terkait) supaya bersih.
  - Baca CSV (kolom: Tanggal, Jenis, Kategori, Dompet, Nominal (Rp),
    Catatan, Kurs USD saat transaksi).
  - Cocokkan Kategori & Dompet ke data milik user (berdasarkan nama).
  - Simpan tiap baris sebagai Transaction dengan waktu 00:00:00
    (CSV tidak punya komponen jam).
"""

import csv
import sys
from datetime import date as date_type, datetime, time as time_type

# Pastikan root proyek ada di path saat dijalankan dari mana pun
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction

# Peta Jenis (Bahasa Indonesia di CSV) → kind internal
PETA_JENIS = {"Pemasukan": "income", "Pengeluaran": "expense"}


def impor(path_csv, email):
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"[GAGAL] User dengan email {email} tidak ditemukan.")
            return 1

        # --- Bangun peta nama → objek (case-insensitive) milik user ---
        wallet_map = {w.name.strip().lower(): w for w in Wallet.query.filter_by(user_id=user.id)}
        kategori_map = {c.name.strip().lower(): c for c in Category.query.filter_by(user_id=user.id)}

        # --- Hapus transaksi lama + fakta DWH terkait user ini ---
        n_lama = Transaction.query.filter_by(user_id=user.id).delete()
        try:
            from app.models.dwh import FactTransaction
            FactTransaction.query.filter_by(user_id=user.id).delete()
        except Exception:
            pass  # tabel DWH boleh belum ada
        db.session.commit()
        print(f"[INFO] Menghapus {n_lama} transaksi lama milik {user.name}.")

        # --- Baca & masukkan CSV ---
        dimasukkan = 0
        dilewati = []
        with open(path_csv, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):  # baris 2 = data pertama
                jenis = (row.get("Jenis") or "").strip()
                kind = PETA_JENIS.get(jenis)
                if not kind:
                    dilewati.append((i, f"Jenis tidak dikenal: {jenis!r}"))
                    continue

                nama_kat = (row.get("Kategori") or "").strip()
                nama_wal = (row.get("Dompet") or "").strip()
                kat = kategori_map.get(nama_kat.lower())
                wal = wallet_map.get(nama_wal.lower())
                if not kat:
                    dilewati.append((i, f"Kategori tidak ada: {nama_kat!r}"))
                    continue
                if not wal:
                    dilewati.append((i, f"Dompet tidak ada: {nama_wal!r}"))
                    continue

                try:
                    nominal = int(float((row.get("Nominal (Rp)") or "0").strip()))
                except ValueError:
                    dilewati.append((i, "Nominal tidak valid"))
                    continue

                try:
                    tgl = date_type.fromisoformat((row.get("Tanggal") or "").strip())
                except ValueError:
                    dilewati.append((i, "Tanggal tidak valid"))
                    continue

                # CSV tidak punya jam → set ke 00:00:00
                dt = datetime.combine(tgl, time_type(0, 0, 0))

                # Kurs USD: hanya relevan untuk income (dasar fitur erosi)
                kurs_raw = (row.get("Kurs USD saat transaksi") or "").strip()
                usd_rate = None
                if kurs_raw:
                    try:
                        usd_rate = float(kurs_raw)
                    except ValueError:
                        usd_rate = None

                # Catatan: "-" dianggap kosong
                catatan = (row.get("Catatan") or "").strip()
                if catatan == "-":
                    catatan = None

                trx = Transaction(
                    user_id=user.id,
                    wallet_id=wal.id,
                    category_id=kat.id,
                    amount=nominal,
                    kind=kind,
                    date=dt,
                    note=catatan,
                    usd_rate_at_date=usd_rate,
                )
                db.session.add(trx)
                dimasukkan += 1

        db.session.commit()
        print(f"[SUKSES] {dimasukkan} transaksi dimasukkan untuk {user.name} ({email}).")
        if dilewati:
            print(f"[PERINGATAN] {len(dilewati)} baris dilewati:")
            for baris, alasan in dilewati:
                print(f"   - baris {baris}: {alasan}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Pakai: python scripts/import_keuangan_csv.py "<file.csv>" <email>')
        sys.exit(2)
    sys.exit(impor(sys.argv[1], sys.argv[2]))
