import time
from datetime import date, datetime, timedelta

import requests

# yfinance bersifat OPSIONAL.
# Di lingkungan serverless (mis. Vercel) paket ini beserta dependensinya
# (pandas/numpy/lxml) terlalu besar dan memperlambat cold start, sehingga
# sengaja TIDAK dipasang di sana. Bila yfinance tidak tersedia, `yf` = None
# dan setiap pemanggilan `yf.<...>` akan melempar AttributeError yang langsung
# ditangkap oleh blok `except Exception` di tiap fungsi → otomatis jatuh ke
# fallback API HTTP gratis. Jadi fitur market tetap berjalan tanpa yfinance.
try:
    import yfinance as yf
except ImportError:  # pragma: no cover - jalur khusus lingkungan tanpa yfinance
    yf = None

# Cache sederhana in-memory per key data
_cache = {}
CACHE_TTL = 3600  # 1 jam

# Jumlah gram dalam 1 troy ounce (untuk konversi harga emas oz → gram)
GRAM_PER_OUNCE = 31.1035


def _now_iso():
    """Waktu sekarang (zona waktu lokal) dalam format ISO — untuk label 'terakhir diperbarui'."""
    return datetime.now().astimezone().isoformat(timespec="seconds")

# Timeout untuk request HTTP ke API gratis (detik)
_HTTP_TIMEOUT = 10

# Sumber fallback HTTP gratis tanpa API key.
# Dipakai saat yfinance gagal (mis. kena rate-limit "Too Many Requests").
_ERAPI_LATEST = "https://open.er-api.com/v6/latest/USD"
_FRANKFURTER_LATEST = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=IDR"
_FRANKFURTER_RANGE = "https://api.frankfurter.dev/v1/{start}..{end}?base=USD&symbols=IDR"
_GOLD_API = "https://api.gold-api.com/price/XAU"  # harga emas USD per troy ounce


def _cache_valid(key):
    """Cek apakah cache untuk key tertentu masih berlaku."""
    entry = _cache.get(key)
    return entry and (time.time() - entry["ts"]) < CACHE_TTL


def _http_fallback_enabled():
    """
    Apakah boleh memanggil API HTTP eksternal sebagai fallback?
    Dimatikan saat testing (TestConfig) agar test tidak butuh koneksi internet.
    """
    try:
        from flask import current_app
        return current_app.config.get("MARKET_HTTP_FALLBACK", True)
    except Exception:
        # Di luar konteks Flask → izinkan (dipakai mis. saat dijalankan manual)
        return True


def _fetch_usd_idr_http():
    """
    Ambil kurs USD/IDR dari API HTTP gratis (tanpa key) sebagai fallback.
    Mencoba beberapa sumber berurutan. Kembalikan float atau None.
    """
    # Sumber 1: open.er-api.com
    try:
        r = requests.get(_ERAPI_LATEST, timeout=_HTTP_TIMEOUT)
        d = r.json()
        if d.get("result") == "success":
            rate = d.get("rates", {}).get("IDR")
            if rate:
                return float(rate)
    except Exception:
        pass

    # Sumber 2: frankfurter.dev
    try:
        r = requests.get(_FRANKFURTER_LATEST, timeout=_HTTP_TIMEOUT)
        rate = r.json().get("rates", {}).get("IDR")
        if rate:
            return float(rate)
    except Exception:
        pass

    return None


def get_usd_idr():
    """
    Ambil kurs USD/IDR terkini.
    Urutan sumber: yfinance (IDR=X) → API HTTP gratis → cache lama.
    Cache 1 jam. Kembalikan {"rate": float|None, "source": str, "cached": bool}.
    """
    key = "usd_idr"
    if _cache_valid(key):
        return _cache[key]["data"]

    # Sumber utama: yfinance
    try:
        ticker = yf.Ticker("IDR=X")
        hist = ticker.history(period="2d")
        if hist.empty:
            raise ValueError("Data IDR=X kosong dari yfinance")
        rate = float(hist["Close"].iloc[-1])
        data = {"rate": rate, "source": "yfinance", "cached": False, "fetched_at": _now_iso()}
        _cache[key] = {"data": data, "ts": time.time()}
        return data

    except Exception:
        # Fallback 1: API HTTP gratis (mis. saat yfinance kena rate-limit)
        if _http_fallback_enabled():
            rate = _fetch_usd_idr_http()
            if rate:
                data = {"rate": rate, "source": "exchange-api", "cached": False, "fetched_at": _now_iso()}
                _cache[key] = {"data": data, "ts": time.time()}
                return data

        # Fallback 2: cache lama bila ada
        if key in _cache:
            fallback = dict(_cache[key]["data"])
            fallback["cached"] = True
            fallback["source"] = "fallback"
            return fallback

        return {"rate": None, "source": "unavailable", "cached": False, "fetched_at": None}


def _fetch_gold_usd_http():
    """Ambil harga emas (USD per troy ounce) dari gold-api.com. Float atau None."""
    try:
        r = requests.get(_GOLD_API, timeout=_HTTP_TIMEOUT)
        price = r.json().get("price")
        if price:
            return float(price)
    except Exception:
        pass
    return None


def get_gold():
    """
    Ambil harga emas terkini (per troy ounce) dan konversi ke IDR.
    Urutan sumber emas: yfinance (GC=F) → gold-api.com → cache lama.
    Konversi memakai kurs dari get_usd_idr() (yang juga punya fallback sendiri).
    Cache 1 jam. Kembalikan {"price_idr": int|None, "source": str, "cached": bool}.
    """
    key = "gold"
    if _cache_valid(key):
        return _cache[key]["data"]

    try:
        usd_idr = get_usd_idr().get("rate")
        if not usd_idr:
            raise ValueError("Kurs USD/IDR tidak tersedia untuk konversi emas")

        # Sumber utama: yfinance (GC=F dalam USD per troy ounce)
        usd_per_oz = None
        try:
            ticker = yf.Ticker("GC=F")
            hist = ticker.history(period="2d")
            if not hist.empty:
                usd_per_oz = float(hist["Close"].iloc[-1])
        except Exception:
            usd_per_oz = None

        source = "yfinance"
        # Fallback: gold-api.com bila yfinance gagal
        if usd_per_oz is None and _http_fallback_enabled():
            usd_per_oz = _fetch_gold_usd_http()
            source = "gold-api"

        if usd_per_oz is None:
            raise ValueError("Harga emas tidak tersedia dari sumber manapun")

        idr_per_oz = usd_per_oz * usd_idr
        # Sertakan juga harga per gram agar konsisten dengan fitur investasi emas
        data = {
            "price_idr": round(idr_per_oz),
            "price_idr_per_gram": round(idr_per_oz / GRAM_PER_OUNCE),
            "source": source,
            "cached": False,
            "fetched_at": _now_iso(),
        }
        _cache[key] = {"data": data, "ts": time.time()}
        return data

    except Exception:
        if key in _cache:
            fallback = dict(_cache[key]["data"])
            fallback["cached"] = True
            fallback["source"] = "fallback"
            return fallback
        return {
            "price_idr": None,
            "price_idr_per_gram": None,
            "source": "unavailable",
            "cached": False,
            "fetched_at": None,
        }


def _fetch_usd_idr_history_http(months):
    """
    Ambil riwayat kurs USD/IDR dari frankfurter.dev (fallback tanpa key).
    Kembalikan list [{"date","rate"}, ...] urut tanggal naik, atau [].
    """
    try:
        end = date.today()
        # Perkiraan kasar: ~31 hari per bulan agar rentang cukup
        start = end - timedelta(days=months * 31)
        url = _FRANKFURTER_RANGE.format(start=start.isoformat(), end=end.isoformat())
        r = requests.get(url, timeout=_HTTP_TIMEOUT + 5)
        rates = r.json().get("rates", {})
        result = [
            {"date": tgl, "rate": float(v["IDR"])}
            for tgl, v in rates.items()
            if v.get("IDR")
        ]
        result.sort(key=lambda x: x["date"])
        return result
    except Exception:
        return []


def get_usd_idr_history(months=6):
    """
    Ambil riwayat kurs USD/IDR selama N bulan.
    Urutan sumber: yfinance (IDR=X) → frankfurter.dev → cache lama → [].
    Kembalikan list [{"date": "YYYY-MM-DD", "rate": float}, ...] urut tanggal naik.
    """
    key = f"usd_idr_history_{months}"
    if _cache_valid(key):
        return _cache[key]["data"]

    try:
        ticker = yf.Ticker("IDR=X")
        hist = ticker.history(period=f"{months}mo")
        if hist.empty:
            raise ValueError("Riwayat IDR=X kosong dari yfinance")

        # Susun list tanggal-rate urut naik
        result = []
        for tanggal, baris in hist.iterrows():
            result.append({
                "date": tanggal.strftime("%Y-%m-%d"),
                "rate": float(baris["Close"]),
            })
        result.sort(key=lambda x: x["date"])

        _cache[key] = {"data": result, "ts": time.time()}
        return result

    except Exception:
        # Fallback 1: frankfurter.dev
        if _http_fallback_enabled():
            result = _fetch_usd_idr_history_http(months)
            if result:
                _cache[key] = {"data": result, "ts": time.time()}
                return result

        # Fallback 2: cache lama bila ada
        if key in _cache:
            return _cache[key]["data"]
        return []


def _fetch_usd_idr_at_date_http(target_date):
    """
    Ambil kurs USD/IDR pada satu tanggal tertentu dari frankfurter.dev (fallback).
    Frankfurter otomatis memundurkan ke hari kerja terdekat bila tanggal libur.
    Kembalikan float atau None.
    """
    try:
        url = f"https://api.frankfurter.dev/v1/{target_date.isoformat()}?base=USD&symbols=IDR"
        r = requests.get(url, timeout=_HTTP_TIMEOUT)
        rate = r.json().get("rates", {}).get("IDR")
        if rate:
            return float(rate)
    except Exception:
        pass
    return None


def get_usd_idr_at_date(target_date):
    """
    Ambil kurs USD/IDR pada (atau terdekat SEBELUM) tanggal tertentu.

    Dipakai fitur erosi nilai agar memakai kurs SAAT transaksi terjadi —
    bukan kurs hari ini — sehingga erosi untuk transaksi lama tetap akurat.

    Urutan sumber: yfinance (IDR=X) → frankfurter.dev → kurs sekarang (terakhir).
    Kembalikan float atau None.
    """
    # Normalisasi ke objek date
    if isinstance(target_date, datetime):
        target_date = target_date.date()

    # Tanggal hari ini atau masa depan → pakai kurs terkini saja
    if target_date >= date.today():
        return get_usd_idr().get("rate")

    key = f"usd_at_{target_date.isoformat()}"
    if _cache_valid(key):
        return _cache[key]["data"]

    rate = None
    # Sumber utama: yfinance — ambil jendela ~7 hari, pakai harga terakhir <= target
    try:
        ticker = yf.Ticker("IDR=X")
        mulai = target_date - timedelta(days=7)
        akhir = target_date + timedelta(days=1)
        hist = ticker.history(start=mulai.isoformat(), end=akhir.isoformat())
        if not hist.empty:
            rate = float(hist["Close"].iloc[-1])
    except Exception:
        rate = None

    # Fallback: frankfurter.dev untuk tanggal tersebut
    if rate is None and _http_fallback_enabled():
        rate = _fetch_usd_idr_at_date_http(target_date)

    # Fallback terakhir: kurs sekarang (lebih baik daripada tidak ada sama sekali)
    if rate is None:
        rate = get_usd_idr().get("rate")

    if rate is not None:
        _cache[key] = {"data": rate, "ts": time.time()}
    return rate


def get_gold_per_gram():
    """
    Harga emas terkini dalam Rupiah per gram (dari get_gold()).
    Kembalikan {"price_idr": int|None, "source": str, "cached": bool, "fetched_at": str|None}.
    """
    g = get_gold()
    per_gram = g.get("price_idr_per_gram")
    if per_gram is None and g.get("price_idr") is not None:
        per_gram = round(g["price_idr"] / GRAM_PER_OUNCE)
    return {
        "price_idr": per_gram,
        "source": g.get("source"),
        "cached": g.get("cached", False),
        "fetched_at": g.get("fetched_at"),
    }


def get_gold_history(months=6):
    """
    Riwayat harga emas dalam Rupiah per gram selama N bulan.

    Mengambil harga emas (GC=F, USD/oz) dan kurs USD/IDR (IDR=X) dari yfinance,
    lalu menyelaraskan per tanggal: idr_per_gram = usd_per_oz * kurs / 31,1035.
    Kembalikan list [{"date": "YYYY-MM-DD", "price_idr": int}, ...] urut tanggal naik.
    """
    key = f"gold_history_{months}"
    if _cache_valid(key):
        return _cache[key]["data"]

    try:
        gold_hist = yf.Ticker("GC=F").history(period=f"{months}mo")
        fx_hist = yf.Ticker("IDR=X").history(period=f"{months}mo")
        if gold_hist.empty:
            raise ValueError("Riwayat emas (GC=F) kosong dari yfinance")

        # Peta tanggal → kurs USD/IDR untuk konversi per hari
        fx_map = {
            idx.strftime("%Y-%m-%d"): float(baris["Close"])
            for idx, baris in fx_hist.iterrows()
        }

        result = []
        kurs_terakhir = None  # dipakai bila tanggal emas tak punya kurs (mis. hari libur kurs)
        for idx, baris in gold_hist.iterrows():
            tgl = idx.strftime("%Y-%m-%d")
            kurs = fx_map.get(tgl) or kurs_terakhir
            if kurs:
                kurs_terakhir = kurs
            else:
                continue  # belum ada kurs sama sekali → lewati titik ini
            idr_per_gram = float(baris["Close"]) * kurs / GRAM_PER_OUNCE
            result.append({"date": tgl, "price_idr": round(idr_per_gram)})

        result.sort(key=lambda x: x["date"])
        _cache[key] = {"data": result, "ts": time.time()}
        return result

    except Exception:
        # Fallback: cache lama bila ada, jika tidak list kosong
        if key in _cache:
            return _cache[key]["data"]
        return []


def reset_cache():
    """Kosongkan seluruh cache — dipakai di test."""
    _cache.clear()
