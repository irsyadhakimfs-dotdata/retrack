"""Test unit erosion_service — verifikasi rumus erosi nilai."""
import pytest
from app.services.erosion_service import hitung_erosi


class TestHitungErosi:
    def test_kurs_naik_erosi_positif(self):
        """Kurs naik (Rupiah melemah) → erosi positif (daya beli turun)."""
        # 5.000.000 Rp @ 15.000 → 16.000 = -6,25%
        hasil = hitung_erosi(5_000_000, 15_000, 16_000)
        assert hasil is not None
        assert abs(hasil["erosi_persen"] - 6.25) < 0.01

    def test_nilai_usd_awal(self):
        """nilai_usd_awal harus 5.000.000 / 15.000 = 333,3333."""
        hasil = hitung_erosi(5_000_000, 15_000, 16_000)
        assert abs(hasil["nilai_usd_awal"] - 333.3333) < 0.01

    def test_nilai_usd_sekarang(self):
        """nilai_usd_sekarang harus 5.000.000 / 16.000 = 312,50."""
        hasil = hitung_erosi(5_000_000, 15_000, 16_000)
        assert abs(hasil["nilai_usd_sekarang"] - 312.50) < 0.01

    def test_kurs_turun_erosi_negatif(self):
        """Kurs turun (Rupiah menguat) → erosi negatif (daya beli naik)."""
        hasil = hitung_erosi(5_000_000, 16_000, 15_000)
        assert hasil["erosi_persen"] < 0

    def test_kurs_datar_erosi_nol(self):
        """Kurs tidak berubah → erosi tepat 0."""
        hasil = hitung_erosi(5_000_000, 15_000, 15_000)
        assert hasil["erosi_persen"] == 0.0

    def test_kurs_awal_nol_return_none(self):
        """kurs_awal = 0 → kembalikan None (hindari ZeroDivisionError)."""
        assert hitung_erosi(5_000_000, 0, 16_000) is None

    def test_kurs_none_return_none(self):
        """kurs_sekarang = None → kembalikan None."""
        assert hitung_erosi(5_000_000, 15_000, None) is None
