"""
Generator dataset realistis untuk persona "Andi" (karyawan muda hemat).

Menghasilkan transaksi Jan 2025 s.d. hari ini ke CSV berformat sama dengan
injectable lainnya. Deterministik (seed tetap) -> output dapat direproduksi.
Saldo tiap dompet dijamin non-negatif by construction (lihat build_dataset).
"""
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


def build_dataset(seed=SEED):
    """
    Bangun daftar baris transaksi (list of dict berkunci HEADER).

    Strategi non-negatif: simpan saldo berjalan tiap dompet. Untuk pengeluaran,
    pilih dompet "prefer"; bila saldonya tak cukup, jatuhkan ke BSI yang selalu
    terdanai gaji awal bulan. Gaji dicatat tanggal 1 tiap bulan (uang masuk lebih
    dulu sebelum dibelanjakan) sehingga BSI tak pernah minus.
    """
    rng = random.Random(seed)
    bal = dict(WALLET_INITIAL)
    rows = []

    def add_income(d, kat, wallet, amount, note):
        bal[wallet] += amount
        rows.append({
            "Tanggal": d.isoformat(), "Jenis": "Pemasukan",
            "Kategori": kat, "Dompet": wallet,
            "Nominal (Rp)": str(amount), "Catatan": note,
            "Kurs USD saat transaksi": kurs_for(d),
        })

    def add_expense(d, kat, prefer, amount, note):
        wallet = prefer if bal[prefer] >= amount else "BSI"
        bal[wallet] -= amount
        rows.append({
            "Tanggal": d.isoformat(), "Jenis": "Pengeluaran",
            "Kategori": kat, "Dompet": wallet,
            "Nominal (Rp)": str(amount), "Catatan": note,
            "Kurs USD saat transaksi": "",
        })

    d = START
    while d <= END:
        dom = d.day

        # === PEMASUKAN dulu (awal bulan) ===
        if dom == 1:
            for w, amt in gaji_split(d):
                add_income(d, "Gaji", w, amt, "gaji bulan ini")
        # THR menjelang Lebaran (income, sebagian ditabung ke Bank Jago)
        if d == date(2025, 3, 20):
            add_income(d, "THR/Bonus", "BSI", 2_500_000, "THR Lebaran")
            add_income(d, "THR/Bonus", "Bank Jago", 1_000_000, "THR ditabung")
        if d == date(2026, 3, 12):
            add_income(d, "THR/Bonus", "BSI", 2_700_000, "THR Lebaran")
            add_income(d, "THR/Bonus", "Bank Jago", 1_000_000, "THR ditabung")
        # Cashback sporadis
        if rng.random() < 0.05:
            add_income(d, "Cashback", rng.choice(["Gopay", "Dana"]),
                       rng.randrange(2_000, 15_001, 1_000), "cashback promo")

        # === PENGELUARAN HARIAN ===
        if rng.random() < 0.92:
            n_meals = 1 + (1 if rng.random() < 0.30 else 0)
            for _ in range(n_meals):
                prefer = rng.choices(["BSI", "Gopay", "Cash", "Dana"],
                                     weights=[50, 30, 15, 5])[0]
                add_expense(d, "Makanan", prefer,
                            rng.randrange(12_000, 25_001, 500),
                            rng.choice(FOOD_NOTES))
        if rng.random() < 0.40:
            add_expense(d, "Bensin", "BSI",
                        rng.randrange(10_000, 20_001, 1_000),
                        rng.choice(BENSIN_NOTES))
        if rng.random() < 0.35:
            prefer = rng.choices(["Gopay", "Cash", "Dana"], weights=[50, 30, 20])[0]
            add_expense(d, "Kopi & Jajan", prefer,
                        rng.randrange(8_000, 25_001, 500),
                        rng.choice(KOPI_NOTES))
        if rng.random() < 0.06:
            add_expense(d, "Transportasi", "Cash",
                        rng.choice([2_000, 3_000, 5_000, 35_000, 50_000]),
                        rng.choice(["parkir", "servis motor", "tambal ban"]))
        if rng.random() < 0.07:
            add_expense(d, "Belanja", "BSI",
                        rng.randrange(25_000, 150_001, 5_000),
                        rng.choice(["sabun & shampoo", "kebutuhan kos", "belanja bulanan"]))
        if rng.random() < 0.03:
            add_expense(d, "Kesehatan", "BSI",
                        rng.randrange(20_000, 120_001, 5_000),
                        rng.choice(["obat", "vitamin", "periksa"]))
        if rng.random() < 0.05:
            add_expense(d, "Hiburan", rng.choice(["Gopay", "Dana"]),
                        rng.randrange(15_000, 100_001, 5_000),
                        rng.choice(["nonton", "langganan streaming", "main"]))

        # === TAGIHAN BULANAN (tanggal tetap) ===
        if dom == 5:
            add_expense(d, "Kos", "BSI", 650_000, "bayar kos bulan ini")
        if dom == 10:
            add_expense(d, "Listrik & Air", "BSI",
                        rng.randrange(80_000, 120_001, 5_000), "token listrik & air")
        if dom == 12:
            add_expense(d, "Internet & Pulsa", "BSI",
                        rng.randrange(80_000, 120_001, 5_000), "paket internet & pulsa")
        if dom == 27:
            add_expense(d, "Transfer Keluarga", "BSI",
                        rng.choice([200_000, 250_000, 300_000, 400_000]),
                        "kirim untuk keluarga")
        if dom == 28:
            add_expense(d, "Nabung", "BSI",
                        rng.choice([200_000, 300_000, 400_000]), "sisihkan tabungan")

        d += timedelta(days=1)

    return rows


def min_balances(rows):
    """
    Replay independen: kembalikan dict {nama_dompet: saldo_minimum} sepanjang
    periode, dihitung ulang dari WALLET_INITIAL. Pengecekan ini terpisah dari
    logika build_dataset agar bug greedy ketahuan.
    """
    bal = dict(WALLET_INITIAL)
    mins = dict(WALLET_INITIAL)
    for r in rows:
        amt = int(r["Nominal (Rp)"])
        w = r["Dompet"]
        if r["Jenis"] == "Pemasukan":
            bal[w] += amt
        else:
            bal[w] -= amt
        mins[w] = min(mins[w], bal[w])
    return mins
