# 03 — Halaman Frontend & Acuan Desain

Acuan desain dari Google Stitch (`docs/stitch/`). Semua halaman mewarisi
`base.html` (navbar/sidebar + toggle dark mode).

## Sistem Desain
Font **Manrope** (Google Fonts). Warna via CSS variables:
```css
:root{
  --bg:#F8FAFC; --card:#FFFFFF; --text:#0F172A; --text-2:#64748B;
  --btn:#0F172A; --accent:#2563EB; --pos:#059669; --neg:#E11D48; --border:#E2E8F0;
}
[data-theme="dark"]{
  --bg:#020617; --card:#0F172A; --text:#F8FAFC; --text-2:#94A3B8;
  --btn:#2563EB; --accent:#2563EB; --pos:#34D399; --neg:#FB7185; --border:#334155;
}
```
Responsive wajib (sidebar → hamburger/bottom-nav di mobile). Prinsip: bersih,
minimalis, sedikit klik, grafik diutamakan.

## Halaman & Komponen Kunci
| Halaman | Komponen |
|---------|----------|
| Login/Register | form email+password, validasi, link antar halaman |
| Dashboard | kartu saldo, income/expense bulan ini, progress budget, daftar goal, grafik mingguan |
| Transaksi | daftar+filter+search+tombol aksi; **baris income punya badge hover erosi** |
| Tambah/Edit Transaksi | form nominal, jenis, tanggal, kategori, wallet, catatan (boleh modal) |
| Kategori | tab income/expense, ikon+nama, tambah/edit/hapus |
| Budget | limit + progress bar + status warna (aman/hampir/lewat) |
| Wallets | kartu wallet + saldo, tambah/edit/hapus |
| Goals | kartu goal + progress ring/bar + tombol setor |
| Laporan | line (tren), pie (komposisi), bar (antar bulan), pemilih periode |
| Market | kartu kurs USD/IDR, kartu+grafik emas, pesan fallback API gagal |
| Pengaturan | profil, ganti password, export CSV, toggle dark mode |

## Fitur Hover Erosi (di halaman Transaksi)
Pada baris pemasukan, saat hover tampilkan tooltip/badge berisi % daya beli
terhadap USD yang tergerus sejak tanggal transaksi, mis.
"↓ 6,25% vs USD sejak 1 Mei (kurs 15.000 → 16.000)". Data dari field `erosi`
pada response API. Beri keterangan kecil: mengukur terhadap USD, bukan inflasi
domestik. Jika `usd_rate_at_date` kosong → "data kurs tidak tersedia".

## Chart.js
Konfigurasi di `static/js/charts.js`, data dari `/api/reports/*`. Warna ambil
dari CSS variable (via getComputedStyle) agar selaras tema.
