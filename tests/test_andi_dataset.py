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
        # Kategori & dompet subset yang didefinisikan
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


def test_saldo_tak_pernah_negatif():
    rows = gen.build_dataset()
    mins = gen.min_balances(rows)
    # Setiap dompet punya saldo minimum >= 0 sepanjang periode
    for name, _, _ in gen.WALLETS:
        assert mins[name] >= 0, f"Dompet {name} pernah negatif: {mins[name]}"
