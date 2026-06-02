# 04 — Fitur Erosi Nilai terhadap Kurs (bagian MVP)

## Konsep
Saat hover pada pemasukan Rupiah tanggal X, tampilkan berapa **persen daya beli
terhadap USD** yang sudah tergerus dari tanggal X sampai sekarang.

## Contoh Kasus
- 1 Mei: terima Rp 5.000.000, kurs 15.000/USD → 333,33 USD.
- 22 Mei: kurs 16.000/USD → 312,50 USD.
- Erosi = (333,33 − 312,50)/333,33 × 100 = **−6,25%** (daya beli turun).
- Badge hover: "Daya beli terhadap USD turun 6,25% sejak 1 Mei".

## Rumus
```
nilai_usd_awal     = jumlah_rupiah / kurs_saat_tanggal_X
nilai_usd_sekarang = jumlah_rupiah / kurs_sekarang
erosi_persen       = (nilai_usd_awal - nilai_usd_sekarang) / nilai_usd_awal * 100
```
Positif = daya beli turun (Rupiah melemah). Negatif = naik (menguat).

## Data
1. Kurs tanggal X → `Transaction.usd_rate_at_date`, diisi saat transaksi income
   dibuat (dari market_service).
2. Kurs sekarang → market_service.
3. "Sisa uang" versi MVP: pakai jumlah pemasukan penuh (pengaitan ke
   pengeluaran tertentu = pengembangan lanjut).

## Lapisan & File
- `services/erosion_service.py` → `hitung_erosi(jumlah_rupiah, kurs_awal,
  kurs_sekarang)` mengembalikan `{nilai_usd_awal, nilai_usd_sekarang,
  erosi_persen}`.
- `api/transactions.py` → sertakan `erosi` di GET income.
- Frontend (halaman Transaksi) → tooltip/badge saat hover.

## Catatan Teknis Penting
API kurs gratis sering tidak punya kurs historis, maka kurs **disimpan saat
transaksi dibuat**, bukan ditarik ulang. Untuk transaksi lama tanpa data,
sediakan input manual kurs (opsional). Karena erosi masuk MVP, **market_service
harus jalan sebelum membuat transaksi income** — itu sebabnya market_service &
erosion_service dikerjakan di sesi yang sama (Fase 3d).

## Acceptance Criteria
- Transaksi income menyimpan kurs tanggal transaksi.
- Hover menampilkan % erosi yang benar (contoh 15.000→16.000 = −6,25%).
- Kurs tidak tersedia → "data kurs tidak tersedia" tanpa crash.
- Unit test `hitung_erosi` untuk skenario naik, turun, datar.
