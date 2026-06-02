def hitung_erosi(jumlah_rupiah, kurs_awal, kurs_sekarang):
    """
    Hitung erosi daya beli pemasukan Rupiah terhadap USD.

    Rumus:
        nilai_usd_awal     = jumlah_rupiah / kurs_awal
        nilai_usd_sekarang = jumlah_rupiah / kurs_sekarang
        erosi_persen       = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal * 100

    Positif  = daya beli turun (Rupiah melemah terhadap USD).
    Negatif  = daya beli naik (Rupiah menguat).
    Nol      = kurs tidak berubah.

    Contoh: 5.000.000 Rp, kurs 15.000 → 16.000 = -6,25% (turun).
    """
    if not kurs_awal or not kurs_sekarang or kurs_awal == 0:
        return None

    nilai_usd_awal = jumlah_rupiah / kurs_awal
    nilai_usd_sekarang = jumlah_rupiah / kurs_sekarang
    erosi_persen = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal * 100

    return {
        "nilai_usd_awal": round(nilai_usd_awal, 4),
        "nilai_usd_sekarang": round(nilai_usd_sekarang, 4),
        "erosi_persen": round(erosi_persen, 4),
    }
