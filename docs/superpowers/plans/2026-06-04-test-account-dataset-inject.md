# Dataset Andi Realistis + Inject Akun Test ke Vercel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hasilkan dataset transaksi "Andi" yang realistis (Jan 2025 → 2026-06-04, ~15 kategori, 5 dompet) lalu suntikkan ke DB produksi Vercel/Neon sebagai akun test `test@retrack.app`.

**Architecture:** Tiga skrip terpisah di `scripts/`: (1) generator deterministik menulis CSV; (2) seeder idempoten membuat user+dompet+kategori; (3) verifier membaca ulang. Import memakai `scripts/import_keuangan_csv.py` yang sudah ada. Tidak ada perubahan di `app/`. Non-negatif saldo dijamin by construction (greedy: setiap pengeluaran diambil dari dompet yang sanggup, kalau tidak jatuh ke BSI yang selalu terdanai gaji awal bulan).

**Tech Stack:** Python 3.11, Flask app factory, SQLAlchemy, pytest, Vercel CLI, Neon Postgres.

**Spec:** `docs/superpowers/specs/2026-06-04-test-account-dataset-inject-design.md`

---

## File Structure

| File | Tanggung jawab |
|---|---|
| `scripts/generate_andi_dataset.py` | Konstanta kanonik (identitas, WALLETS, CATEGORIES, USD_RATES) + `build_dataset()` + `min_balances()` + `write_csv()` + `main()`. Murni data, tak sentuh DB. |
| `scripts/seed_test_account.py` | `seed_test_account()` idempoten + `main()`. Impor konstanta dari generator (DRY). |
| `scripts/verify_test_account.py` | `main()` cetak ringkasan akun (jumlah & saldo). Dipakai untuk dev & prod. |
| `injectable/andi_karyawan_hemat_beli_bensin.csv` | Output generator (ditimpa). |
| `injectable/andi_karyawan_hemat_beli_bensin.orig.csv` | Backup file asli. |
| `tests/test_andi_dataset.py` | Test generator + seeder. |

---

## Task 1: Backup CSV asli

**Files:**
- Create: `injectable/andi_karyawan_hemat_beli_bensin.orig.csv` (salinan file asli)

- [ ] **Step 1: Salin file asli ke .orig**

Run (PowerShell):
```powershell
Copy-Item "injectable/andi_karyawan_hemat_beli_bensin.csv" "injectable/andi_karyawan_hemat_beli_bensin.orig.csv"
```
Expected: file `.orig.csv` ada (58 baris data + header).

- [ ] **Step 2: Verifikasi backup**

Run:
```powershell
(Get-Content "injectable/andi_karyawan_hemat_beli_bensin.orig.csv" | Measure-Object -Line).Lines
```
Expected: `59` (1 header + 58 data).

---

## Task 2: Generator — konstanta & helper

**Files:**
- Create: `scripts/generate_andi_dataset.py`
- Test: `tests/test_andi_dataset.py`

- [ ] **Step 1: Tulis test gagal untuk konstanta**

```python
# tests/test_andi_dataset.py
import os
import sys

# Tambahkan folder scripts ke path agar modul skrip bisa diimpor
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import generate_andi_dataset as gen


def test_konstanta_dasar():
    assert gen.TEST_EMAIL == "test@retrack.app"
    assert gen.TEST_NAME == "Test Data"
    assert gen.TEST_PASSWORD == "12345678"
    # 5 dompet, 15 kategori
    assert len(gen.WALLETS) == 5
    assert len(gen.CATEGORIES) == 15
    # Tipe dompet valid
    assert {t for _, t, _ in gen.WALLETS} <= {"cash", "bank", "ewallet"}
    # Jenis kategori valid
    assert {k for _, k in gen.CATEGORIES} <= {"income", "expense"}


def test_tabel_kurs_lengkap():
    # Setiap bulan dari Jan 2025 s.d. Jun 2026 punya kurs
    for year, mstart, mend in [(2025, 1, 12), (2026, 1, 6)]:
        for m in range(mstart, mend + 1):
            assert (year, m) in gen.USD_RATES
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `python -m pytest tests/test_andi_dataset.py -v`
Expected: FAIL `ModuleNotFoundError: No module named 'generate_andi_dataset'`.

- [ ] **Step 3: Tulis konstanta & helper di generator**

```python
# scripts/generate_andi_dataset.py
"""
Generator dataset realistis untuk persona "Andi" (karyawan muda hemat).

Menghasilkan transaksi Jan 2025 s.d. hari ini ke CSV berformat sama dengan
injectable lainnya. Deterministik (seed tetap) → output dapat direproduksi.
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
```

- [ ] **Step 4: Jalankan test, pastikan LULUS**

Run: `python -m pytest tests/test_andi_dataset.py -v`
Expected: PASS `test_konstanta_dasar`, `test_tabel_kurs_lengkap`.

- [ ] **Step 5: Commit**

```powershell
git add scripts/generate_andi_dataset.py tests/test_andi_dataset.py
git commit -m "feat(scripts): konstanta generator dataset Andi + test"
```

---

## Task 3: Generator — `build_dataset()`

**Files:**
- Modify: `scripts/generate_andi_dataset.py` (tambah fungsi `build_dataset`)
- Test: `tests/test_andi_dataset.py` (tambah test)

- [ ] **Step 1: Tulis test gagal untuk build_dataset**

Tambahkan ke `tests/test_andi_dataset.py`:
```python
def test_build_dataset_struktur():
    rows = gen.build_dataset()
    assert len(rows) > 400  # ~17 bulan data harian
    nama_kat = {n for n, _ in gen.CATEGORIES}
    nama_wal = {n for n, _, _ in gen.WALLETS}
    for r in rows:
        # Semua kolom header ada
        assert set(r.keys()) == set(gen.HEADER)
        # Jenis valid
        assert r["Jenis"] in ("Pemasukan", "Pengeluaran")
        # Kategori & dompet ⊆ yang didefinisikan
        assert r["Kategori"] in nama_kat
        assert r["Dompet"] in nama_wal
        # Tanggal dalam rentang
        from datetime import date as _d
        tgl = _d.fromisoformat(r["Tanggal"])
        assert gen.START <= tgl <= gen.END
        # Kurs: terisi utk income, kosong utk expense
        if r["Jenis"] == "Pemasukan":
            assert r["Kurs USD saat transaksi"] == gen.kurs_for(tgl)
        else:
            assert r["Kurs USD saat transaksi"] == ""


def test_build_dataset_deterministik():
    assert gen.build_dataset() == gen.build_dataset()


def test_ada_gaji_dan_thr():
    rows = gen.build_dataset()
    kategori = [r["Kategori"] for r in rows]
    assert kategori.count("Gaji") >= 17 * 2  # 2 baris gaji per bulan, ~17 bulan
    assert "THR/Bonus" in kategori
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `python -m pytest tests/test_andi_dataset.py::test_build_dataset_struktur -v`
Expected: FAIL `AttributeError: module 'generate_andi_dataset' has no attribute 'build_dataset'`.

- [ ] **Step 3: Implementasi `build_dataset()`**

Tambahkan ke `scripts/generate_andi_dataset.py`:
```python
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
```

- [ ] **Step 4: Jalankan test, pastikan LULUS**

Run: `python -m pytest tests/test_andi_dataset.py -v`
Expected: PASS semua termasuk `test_build_dataset_struktur`, `test_build_dataset_deterministik`, `test_ada_gaji_dan_thr`.

- [ ] **Step 5: Commit**

```powershell
git add scripts/generate_andi_dataset.py tests/test_andi_dataset.py
git commit -m "feat(scripts): build_dataset generator transaksi Andi"
```

---

## Task 4: Generator — jaminan saldo non-negatif

**Files:**
- Modify: `scripts/generate_andi_dataset.py` (tambah `min_balances`)
- Test: `tests/test_andi_dataset.py` (tambah test)

- [ ] **Step 1: Tulis test gagal**

Tambahkan ke `tests/test_andi_dataset.py`:
```python
def test_saldo_tak_pernah_negatif():
    rows = gen.build_dataset()
    mins = gen.min_balances(rows)
    # Setiap dompet punya saldo minimum >= 0 sepanjang periode
    for name, _, _ in gen.WALLETS:
        assert mins[name] >= 0, f"Dompet {name} pernah negatif: {mins[name]}"
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `python -m pytest tests/test_andi_dataset.py::test_saldo_tak_pernah_negatif -v`
Expected: FAIL `AttributeError: ... has no attribute 'min_balances'`.

- [ ] **Step 3: Implementasi `min_balances()`**

Tambahkan ke `scripts/generate_andi_dataset.py`:
```python
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
```

- [ ] **Step 4: Jalankan test, pastikan LULUS**

Run: `python -m pytest tests/test_andi_dataset.py -v`
Expected: PASS semua.

> **Knob (jika test ini GAGAL):** berarti pengeluaran melampaui pemasukan di suatu titik. Perbaikan: naikkan `initial_balance` BSI di `WALLETS`, atau turunkan probabilitas/nominal pengeluaran besar (Belanja/Kesehatan/Transfer/Nabung). Jangan menulis CSV sampai test ini hijau.

- [ ] **Step 5: Commit**

```powershell
git add scripts/generate_andi_dataset.py tests/test_andi_dataset.py
git commit -m "feat(scripts): jaminan saldo non-negatif (min_balances) + test"
```

---

## Task 5: Generator — tulis CSV & hasilkan file

**Files:**
- Modify: `scripts/generate_andi_dataset.py` (tambah `write_csv` + `main`)
- Modify: `injectable/andi_karyawan_hemat_beli_bensin.csv` (di-generate)

- [ ] **Step 1: Implementasi `write_csv()` + `main()`**

Tambahkan ke `scripts/generate_andi_dataset.py`:
```python
import os
import sys

DEFAULT_OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "injectable", "andi_karyawan_hemat_beli_bensin.csv",
)


def write_csv(rows, path=DEFAULT_OUT):
    """Tulis baris ke CSV (quoting penuh, sama gaya file injectable lain)."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(HEADER)
        for r in rows:
            writer.writerow([r[k] for k in HEADER])


def main():
    rows = build_dataset()
    mins = min_balances(rows)
    negatif = {k: v for k, v in mins.items() if v < 0}
    if negatif:
        print(f"[GAGAL] Saldo negatif terdeteksi: {negatif}. CSV tidak ditulis.")
        return 1
    write_csv(rows)
    income = sum(1 for r in rows if r["Jenis"] == "Pemasukan")
    expense = len(rows) - income
    print(f"[SUKSES] {len(rows)} baris ditulis ke {DEFAULT_OUT}")
    print(f"         income={income}, expense={expense}, "
          f"rentang {rows[0]['Tanggal']}..{rows[-1]['Tanggal']}")
    print(f"         saldo minimum per dompet: {mins}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Generate CSV**

Run: `python scripts/generate_andi_dataset.py`
Expected: `[SUKSES] <N> baris ditulis ...` dengan N > 400, rentang `2025-01-01..2026-06-04`, dan `saldo minimum per dompet` semua ≥ 0.

- [ ] **Step 3: Verifikasi file ditimpa dengan benar**

Run:
```powershell
(Get-Content "injectable/andi_karyawan_hemat_beli_bensin.csv" | Measure-Object -Line).Lines
Get-Content "injectable/andi_karyawan_hemat_beli_bensin.csv" -TotalCount 3
```
Expected: jumlah baris = N+1; baris pertama header `"Tanggal","Jenis",...`; baris berikut mulai `"2025-01-01",...`.

- [ ] **Step 4: Commit**

```powershell
git add scripts/generate_andi_dataset.py "injectable/andi_karyawan_hemat_beli_bensin.csv" "injectable/andi_karyawan_hemat_beli_bensin.orig.csv"
git commit -m "feat(data): generate dataset Andi realistis Jan2025-Jun2026 (+backup asli)"
```

---

## Task 6: Seeder akun test (idempoten)

**Files:**
- Create: `scripts/seed_test_account.py`
- Test: `tests/test_andi_dataset.py` (tambah test)

- [ ] **Step 1: Tulis test gagal untuk seeder**

Tambahkan ke `tests/test_andi_dataset.py`:
```python
def test_seed_idempoten(db):
    import seed_test_account as seeder
    from app.models.user import User
    from app.models.wallet import Wallet
    from app.models.category import Category

    # Jalankan dua kali — tidak boleh menduplikasi apa pun
    seeder.seed_test_account()
    seeder.seed_test_account()

    user = User.query.filter_by(email=gen.TEST_EMAIL).first()
    assert user is not None
    assert user.name == gen.TEST_NAME
    assert user.check_password(gen.TEST_PASSWORD)
    assert Wallet.query.filter_by(user_id=user.id).count() == 5
    assert Category.query.filter_by(user_id=user.id).count() == 15
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `python -m pytest tests/test_andi_dataset.py::test_seed_idempoten -v`
Expected: FAIL `ModuleNotFoundError: No module named 'seed_test_account'`.

- [ ] **Step 3: Implementasi seeder**

```python
# scripts/seed_test_account.py
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
              f"(id={user.id}) — {nw} dompet, {nc} kategori.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Jalankan test, pastikan LULUS**

Run: `python -m pytest tests/test_andi_dataset.py -v`
Expected: PASS semua termasuk `test_seed_idempoten`.

- [ ] **Step 5: Commit**

```powershell
git add scripts/seed_test_account.py tests/test_andi_dataset.py
git commit -m "feat(scripts): seeder idempoten akun test (user+dompet+kategori)"
```

---

## Task 7: Verifier akun

**Files:**
- Create: `scripts/verify_test_account.py`

- [ ] **Step 1: Implementasi verifier**

```python
# scripts/verify_test_account.py
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
```

- [ ] **Step 2: Commit**

```powershell
git add scripts/verify_test_account.py
git commit -m "feat(scripts): verifier ringkasan akun test (dev/prod)"
```

---

## Task 8: Dry-run lokal (SQLite dev) — WAJIB sebelum prod

**Files:** tidak ada perubahan kode; menjalankan pipeline penuh di DB dev.

- [ ] **Step 1: Pastikan env dev & DB dev ada**

Run (PowerShell):
```powershell
$env:FLASK_ENV = "development"
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue   # pastikan pakai SQLite lokal
```
Expected: tidak error. (Jika `refinance_dev.db` belum ada, app membuatnya saat start; jika perlu migrasi: `flask db upgrade`.)

- [ ] **Step 2: Seed akun test**

Run: `python scripts/seed_test_account.py`
Expected: `[SUKSES] Akun test siap: Test Data <test@retrack.app> (id=...) — 5 dompet, 15 kategori.`

- [ ] **Step 3: Import CSV**

Run: `python scripts/import_keuangan_csv.py "injectable/andi_karyawan_hemat_beli_bensin.csv" test@retrack.app`
Expected: `[SUKSES] <N> transaksi dimasukkan ...` dengan N = jumlah baris data CSV, dan **TIDAK ada** blok `[PERINGATAN] ... baris dilewati`. (Jika ada baris dilewati → nama Kategori/Dompet di CSV tak cocok dengan seeder; perbaiki sebelum lanjut.)

- [ ] **Step 4: Verifikasi**

Run: `python scripts/verify_test_account.py`
Expected: Dompet 5, Kategori 15, Transaksi = N, Rentang `2025-01-01 .. 2026-06-04`, dan `Saldo: OK (semua >= 0)`.

- [ ] **Step 5: Checkpoint manual**

Konfirmasi angka di Step 3–4 masuk akal sebelum menyentuh produksi. Tidak ada commit (hanya data dev lokal).

---

## Task 9: Tarik kredensial produksi via Vercel CLI

**Files:**
- Modify: `.gitignore` (pastikan `.env.production` diabaikan)

- [ ] **Step 1: Pastikan `.env.production` di-gitignore**

Run:
```powershell
if (-not (Select-String -Path .gitignore -Pattern '^\.env\.production' -Quiet)) {
  Add-Content .gitignore "`n.env.production"
}
Select-String -Path .gitignore -Pattern 'env'
```
Expected: `.env.production` muncul di `.gitignore`. Commit bila berubah:
```powershell
git add .gitignore; git commit -m "chore: gitignore .env.production"
```

- [ ] **Step 2: Install Vercel CLI (bila belum)**

Run: `vercel --version`
Jika belum ada: `npm i -g vercel`
Expected: versi tercetak.

- [ ] **Step 3: Login (DIJALANKAN USER di sesi)**

Minta user mengetik di prompt sesi: `! vercel login`
Expected: login sukses (browser/email).

- [ ] **Step 4: Link proyek**

Run: `vercel link`
Pilih scope + proyek ReTrack yang sudah ada di Vercel. Expected: `.vercel/` dibuat, `Linked to ...`.

- [ ] **Step 5: Tarik environment production**

Run: `vercel env pull .env.production --environment=production`
Expected: file `.env.production` berisi `DATABASE_URL="postgres://...neon..."` dan `SECRET_KEY=...`.

- [ ] **Step 6: Konfirmasi DATABASE_URL terbaca**

Run:
```powershell
(Select-String -Path .env.production -Pattern '^DATABASE_URL=').Line -replace '(://[^:]+:)[^@]+@', '$1***@'
```
Expected: tercetak baris `DATABASE_URL=...` (password ter-mask). Jika kosong → environment/DB belum di-set di Vercel; stop & laporkan ke user.

---

## Task 10: Inject ke produksi (Neon) + verifikasi

**Files:** tidak ada perubahan kode; menjalankan pipeline ke DB prod.

- [ ] **Step 1: Set env produksi di shell**

Run (PowerShell):
```powershell
$env:FLASK_ENV = "production"
$env:DATABASE_URL = ((Select-String -Path .env.production -Pattern '^DATABASE_URL=').Line `
    -replace '^DATABASE_URL=', '' -replace '^"', '' -replace '"$', '')
$env:DATABASE_URL.Substring(0, 18)   # cek prefix saja, jangan cetak penuh
```
Expected: prefix `postgres://` atau `postgresql://`. (Config menormalkan `postgres://`→`postgresql://`.)

- [ ] **Step 2: Pastikan driver Postgres terpasang**

Run: `python -c "import psycopg2; print('psycopg2 OK')"`
Jika gagal: `pip install psycopg2-binary==2.9.10`
Expected: `psycopg2 OK`.

- [ ] **Step 3: Seed akun test di PRODUKSI**

Run: `python scripts/seed_test_account.py`
Expected: `[SUKSES] Akun test siap: Test Data <test@retrack.app> (id=...) — 5 dompet, 15 kategori.`
(Idempoten — aman jika user/dompet sudah ada.)

- [ ] **Step 4: Import CSV ke PRODUKSI**

Run: `python scripts/import_keuangan_csv.py "injectable/andi_karyawan_hemat_beli_bensin.csv" test@retrack.app`
Expected: `[SUKSES] <N> transaksi dimasukkan untuk Test Data (test@retrack.app).` tanpa baris dilewati. (Script hanya menghapus transaksi milik `test@retrack.app` — **bukan** akun lain.)

- [ ] **Step 5: Verifikasi DB prod**

Run: `python scripts/verify_test_account.py`
Expected: Dompet 5, Kategori 15, Transaksi = N, rentang `2025-01-01 .. 2026-06-04`, `Saldo: OK (semua >= 0)`.

- [ ] **Step 6: Verifikasi via API live (end-to-end)**

Run (PowerShell — ganti `<DOMAIN>` dengan domain produksi, mis. `retrack.vercel.app`):
```powershell
$body = @{ email = "test@retrack.app"; password = "12345678" } | ConvertTo-Json
$r = Invoke-WebRequest -Uri "https://<DOMAIN>/api/auth/login" -Method Post `
     -ContentType "application/json" -Body $body -SessionVariable sess
$r.Content
$tx = Invoke-WebRequest -Uri "https://<DOMAIN>/api/transactions?days=186" -WebSession $sess
($tx.Content | ConvertFrom-Json).data.Count
```
Expected: login `{"ok": true, ...}`; jumlah transaksi 6 bulan terakhir > 0. Login di browser dengan kredensial test juga menampilkan dashboard berisi data.

- [ ] **Step 7: Bersihkan env shell (hindari kebocoran)**

Run:
```powershell
Remove-Item Env:DATABASE_URL, Env:FLASK_ENV -ErrorAction SilentlyContinue
```
Expected: env terhapus dari sesi.

---

## Task 11: Serahkan deliverable ke user

- [ ] **Step 1: Susun & sampaikan ringkasan**

Sampaikan ke user (isi `<N>` dari hasil verifikasi):
```
Akun test berhasil di-inject ke produksi:

  Email    : test@retrack.app
  Nama     : Test Data
  Password : 12345678

Data: <N> transaksi, 2025-01-01 s/d 2026-06-04, 15 kategori, 5 dompet
(Cash, BSI, Gopay, Dana, Bank Jago). Login di https://<DOMAIN>/login.
```

- [ ] **Step 2: Pertimbangkan simpan memori**

Catat ke memori (project): akun test prod `test@retrack.app` ada di Neon, dataset Andi, di-inject 2026-06-04 — agar tidak terhapus tak sengaja nanti.

---

## Self-Review Notes

- **Spec coverage:** rentang Jan2025→now (Task 3 START/END), perbanyak kategori+dompet (Task 2: 15 kat/5 dompet), CSV realistis (Task 3–5), akun test+pw 12345678 (Task 6), inject via Vercel CLI (Task 9–10), deliverable email/nama/pw (Task 11), dry-run dulu (Task 8), keamanan email hardcoded (Task 6 & 10 Step 4), backup asli (Task 1), kurs erosi (Task 2 USD_RATES + Task 3). ✓
- **Tidak ada perubahan di `app/`** sesuai spec. ✓
- **Konsistensi nama:** `seed_test_account()` dipakai di Task 6 & 8; konstanta `WALLETS/CATEGORIES/TEST_*` didefinisikan Task 2 dan diimpor Task 6; `min_balances()` Task 4 dipakai di `main()` Task 5; `_hitung_saldo` diimpor dari `app.api.wallets` (ada). ✓
- **Catatan deviasi spec:** gaji dicatat **tanggal 1** (bukan 30 seperti file lama) agar saldo non-negatif tanpa menaikkan initial_balance — initial_balance tetap sesuai spec (Cash 150k, BSI 500k, Gopay 50k, Dana 100k, Bank Jago 300k).
