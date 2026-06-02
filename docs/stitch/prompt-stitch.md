# Prompt Google Stitch — 11 Halaman (per halaman, bertahap)

Kerjakan beberapa prompt per hari agar tidak berat. Ekspor tiap halaman ke
HTML/Figma, simpan ke `docs/stitch/`.

## Blok Desain (tempel di AWAL setiap prompt)
> Aplikasi ReFinance, personal financial planner. Font Manrope. Gaya bersih,
> minimalis, sedikit klik, grafik diutamakan. Bahasa Indonesia. Wajib responsive
> desktop & mobile. Sediakan light & dark mode. Light: bg #F8FAFC, card #FFFFFF,
> teks #0F172A, teks sekunder #64748B, tombol utama #0F172A, aksen #2563EB,
> pemasukan #059669, pengeluaran #E11D48, border #E2E8F0. Dark: bg #020617,
> card #0F172A, teks #F8FAFC, teks sekunder #94A3B8, tombol utama #2563EB,
> aksen #2563EB, pemasukan #34D399, pengeluaran #FB7185, border #334155.

---

**1. Login** — Kartu di tengah layar, logo "ReFinance" di atas, field email &
password, tombol utama "Masuk", link "Belum punya akun? Daftar".

**2. Register** — Kartu di tengah, field nama, email, password, konfirmasi
password, tombol "Daftar", link "Sudah punya akun? Masuk".

**3. Dashboard** — Kartu besar total saldo gabungan. Dua kartu kecil pemasukan
(hijau) & pengeluaran (merah) bulan ini. Progress bar pemakaian budget. Daftar
ringkas tujuan tabungan dengan progress. Grafik pengeluaran mingguan. Sidebar
kiri (desktop): Dashboard, Transaksi, Kategori, Budget, Wallets, Goals, Laporan,
Market, Pengaturan; di mobile jadi hamburger/bottom-nav.

**4. Transaksi** — Daftar transaksi (tanggal, kategori, wallet, nominal berwarna
sesuai income/expense), filter bulan & kategori, kolom pencarian, tombol
"+ Tambah". Khusus baris pemasukan: badge/tooltip kecil yang muncul saat hover,
menampilkan persentase daya beli terhadap USD yang tergerus sejak tanggal
transaksi (mis. "↓ 6,25% vs USD sejak 1 Mei").

**5. Tambah/Edit Transaksi** — Form (boleh modal): nominal, jenis (pemasukan/
pengeluaran), tanggal, kategori, wallet, catatan, tombol simpan & batal.

**6. Kategori** — Dua tab/kolom Pemasukan & Pengeluaran, tiap item ikon + nama,
tombol edit/hapus, tombol tambah.

**7. Budget** — Daftar kategori dengan limit bulanan, progress bar berwarna
(aman biru/hijau, hampir kuning ≥80%, lewat merah >100%), angka terpakai/limit.

**8. Wallets** — Kartu per wallet (Tunai/Bank/E-wallet), saldo besar, ikon
jenis, tombol tambah/edit/hapus.

**9. Savings Goals** — Kartu per tujuan: nama, target, terkumpul, progress
ring/bar, estimasi setoran/bulan, deadline, tombol "Setor".

**10. Laporan** — Pemilih periode, grafik garis tren saldo, diagram lingkaran
komposisi kategori pengeluaran, bar chart perbandingan antar bulan.

**11. Market** — Kartu kurs USD/IDR (nilai + panah naik/turun), kartu harga
emas dengan grafik historis (harian/mingguan/bulanan), tampilan "data tidak
tersedia" untuk kondisi API gagal.

*(+ Pengaturan: profil, ganti password, tombol Export CSV, toggle dark mode.)*
