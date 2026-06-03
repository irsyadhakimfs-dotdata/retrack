import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()


class Config:
    """Konfigurasi dasar yang diwarisi semua environment."""
    SECRET_KEY = os.getenv("SECRET_KEY", "ganti-di-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Interval auto-refresh data market di klien (jam)
    MARKET_REFRESH_HOURS = int(os.getenv("MARKET_REFRESH_HOURS", 6))
    # Default periode tren laporan pemasukan/pengeluaran (bulan); rentang wajar 1–6
    TREND_DEFAULT_MONTHS = int(os.getenv("TREND_DEFAULT_MONTHS", 2))
    # Izinkan fallback ke API HTTP gratis (open.er-api, frankfurter, gold-api)
    # saat yfinance gagal/kena rate-limit. Dimatikan di TestConfig.
    MARKET_HTTP_FALLBACK = True


class DevConfig(Config):
    """Konfigurasi untuk pengembangan lokal."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///refinance_dev.db"
    )


class TestConfig(Config):
    """Konfigurasi untuk pengujian — database in-memory agar test cepat & bersih."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    # Matikan panggilan HTTP eksternal saat test agar cepat & tanpa internet
    MARKET_HTTP_FALLBACK = False


def _normalize_db_url(url):
    """
    Samakan skema URL database agar kompatibel dengan SQLAlchemy.
    Penyedia seperti Neon/Vercel Postgres kadang memberi prefix `postgres://`,
    sedangkan SQLAlchemy mewajibkan `postgresql://`. Bila kosong, jatuh ke
    SQLite lokal agar app tidak gagal start.
    """
    if not url:
        return "sqlite:///refinance_dev.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class ProdConfig(Config):
    """Konfigurasi untuk produksi."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.getenv("DATABASE_URL"))

    # Ketahanan koneksi di serverless (Vercel) + Neon Postgres.
    # - pool_pre_ping: tes koneksi sebelum dipakai → hindari error
    #   "server closed the connection unexpectedly" yang umum terjadi saat
    #   instance serverless berpindah dari idle ke aktif.
    # - pool_recycle: daur ulang koneksi sebelum Neon memutusnya karena idle.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}


# Peta nama environment ke kelas konfigurasi
config_by_name = {
    "development": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig,
}
