"""
Entry point untuk Vercel (runtime @vercel/python).

Vercel mencari WSGI callable bernama `app` di file dalam folder /api.
File ini membungkus application factory ReFinance dan mengekspos `app`.

Semua request (lihat vercel.json) diarahkan ke fungsi serverless ini.
"""
import os
import sys

# Pastikan root proyek ada di sys.path agar `import app` berhasil
# (file ini berada di /api, satu level di bawah root).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402

# Di Vercel selalu pakai konfigurasi production (baca DATABASE_URL & SECRET_KEY
# dari Environment Variables dashboard Vercel).
env = os.getenv("FLASK_ENV", "production")
app = create_app(env)

# Bootstrap skema database sekali saat cold start.
# Penyimpanan Vercel bersifat read-only (kecuali /tmp yang efemeral), jadi
# SQLite TIDAK persisten. Gunakan Postgres eksternal (Neon / Vercel Postgres)
# lewat DATABASE_URL. create_all() hanya membuat tabel yang belum ada — aman
# dijalankan berulang dan tidak menghapus data.
if os.getenv("AUTO_CREATE_DB", "1") == "1":
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:  # noqa: BLE001 - jangan sampai gagal start hanya karena ini
        print(f"[warn] AUTO_CREATE_DB gagal: {e}", file=sys.stderr)
