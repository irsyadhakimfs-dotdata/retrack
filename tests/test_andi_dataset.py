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
