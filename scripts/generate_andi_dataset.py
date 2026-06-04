"""
Generator dataset realistis untuk persona "Andi" (karyawan muda hemat).

Menghasilkan transaksi Jan 2025 s.d. hari ini ke CSV berformat sama dengan
injectable lainnya. Deterministik (seed tetap) -> output dapat direproduksi.
Saldo tiap dompet dijamin non-negatif by construction (lihat build_dataset).
"""
import calendar
import csv
import random
from datetime import date, timedelta

# --- Identitas akun test (sumber kebenaran tunggal, dipakai seeder juga) ---
TEST_EMAIL = "test@retrack.app"
TEST_NAME = "Test Data"
TEST_PASSWORD = "12345678"

# --- Rentang & seed ---
START = date(2025, 1, 1)
END = date(2026, 6, 4)
SEED = 20260604

# --- Dompet: (nama, type, initial_balance) ---
WALLETS = [
    ("Cash", "cash", 150_000),
    ("BSI", "bank", 500_000),
    ("Gopay", "ewallet", 50_000),
    ("Dana", "ewallet", 100_000),
    ("Bank Jago", "bank", 300_000),
]

# --- Kategori: (nama, kind) ---
CATEGORIES = [
    ("Gaji", "income"),
    ("THR/Bonus", "income"),
    ("Cashback", "income"),
    ("Makanan", "expense"),
    ("Bensin", "expense"),
    ("Kos", "expense"),
    ("Listrik & Air", "expense"),
    ("Internet & Pulsa", "expense"),
    ("Transportasi", "expense"),
    ("Belanja", "expense"),
    ("Kesehatan", "expense"),
    ("Hiburan", "expense"),
    ("Kopi & Jajan", "expense"),
    ("Transfer Keluarga", "expense"),
    ("Nabung", "expense"),
]

# --- Kurs USD/IDR per bulan (hanya untuk baris income; dasar fitur erosi) ---
USD_RATES = {
    (2025, 1): 16200, (2025, 2): 16300, (2025, 3): 16500, (2025, 4): 16400,
    (2025, 5): 16300, (2025, 6): 16250, (2025, 7): 16200, (2025, 8): 16400,
    (2025, 9): 16600, (2025, 10): 16800, (2025, 11): 17000, (2025, 12): 17200,
    (2026, 1): 17400, (2026, 2): 17500, (2026, 3): 17600, (2026, 4): 17673,
    (2026, 5): 17673, (2026, 6): 17673,
}

HEADER = ["Tanggal", "Jenis", "Kategori", "Dompet",
          "Nominal (Rp)", "Catatan", "Kurs USD saat transaksi"]

WALLET_INITIAL = {name: init for name, _, init in WALLETS}

# Catatan natural Bahasa Indonesia
FOOD_NOTES = ["nasi warteg", "nasi bungkus", "makan siang", "sarapan",
              "mie rebus", "nasi padang", "gado-gado", "soto ayam", "ayam geprek"]
BENSIN_NOTES = ["bensin motor", "isi bensin", "BBM", "pom bensin"]
KOPI_NOTES = ["kopi", "es teh", "gorengan", "jajan", "cemilan", "roti"]


def kurs_for(d):
    """Kurs USD/IDR (string) untuk bulan tanggal d."""
    return str(USD_RATES[(d.year, d.month)])


def gaji_split(d):
    """Pembagian gaji ke dompet; naik mulai September 2025."""
    if (d.year, d.month) >= (2025, 9):
        return [("BSI", 3_000_000), ("Gopay", 750_000)]
    return [("BSI", 2_800_000), ("Gopay", 700_000)]
