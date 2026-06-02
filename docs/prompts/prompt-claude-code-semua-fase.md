# Prompt Claude Code — Semua Fase (copy-paste)

Satu fase = satu sesi baru Claude Code (Fase 3 & 4 dipecah jadi sub-sesi).
Tiap prompt menyebut: fase, file yang disentuh, dokumen acuan, cara uji.

---

## FASE 1 — Setup
Kita mulai Fase 1 (Setup) ReFinance. Baca CLAUDE.md & docs/00-overview.md.
Buat: struktur folder lengkap (app/{models,api,services,views,templates,
static/{css,js,img}}, tests/) dengan __init__.py; requirements.txt (Flask,
Flask-SQLAlchemy, Flask-Migrate, Flask-Login, python-dotenv, requests, pytest);
app/config.py (DevConfig, TestConfig SQLite in-memory, ProdConfig, baca .env);
app/extensions.py (db, migrate, login_manager); app/__init__.py dengan
create_app() + route /ping yang return JSON pong; run.py; .env.example;
.gitignore; README. Komentar # Bahasa Indonesia. Jangan buat model/API dulu.
Uji: flask run → /ping return pong tanpa error. Ingatkan saya commit.

---

## FASE 2 — Database
Kita di Fase 2 (Database) ReFinance. Acuan docs/01-database-schema.md. Buat
semua model di app/models/ (User, Wallet, Category, Transaction, Budget,
SavingsGoal) dengan relasi sesuai dokumen. Uang sebagai Integer. User punya
set_password/check_password + UserMixin. Transaction punya kolom
usd_rate_at_date (Float) — WAJIB untuk income (fitur erosi masuk MVP). Siapkan
Flask-Migrate, buat & terapkan migrasi awal. Tulis tests/conftest.py (fixture
app TestConfig + db sementara + client) dan tests/test_models.py. Jangan sentuh
api/services/views. Uji: migrasi sukses + pytest tests/test_models.py PASS.
Ingatkan commit.

---

## FASE 3 — API Backend (pecah 4 sesi)

### 3a — Auth API
Fase 3a (Auth API) ReFinance. Acuan docs/02-api-spec.md (Auth) + model user.
Buat app/api/auth.py (register/login/logout), format {ok,data}/{ok,error},
integrasi Flask-Login, daftarkan blueprint. Test: register, login benar/salah,
akses terproteksi tanpa login ditolak. Jangan ubah file lain. Uji pytest PASS,
ingatkan commit.

### 3b — Wallets, Categories, Transactions
Fase 3b ReFinance. Acuan docs/02-api-spec.md + 01-database-schema.md. Buat
app/api/wallets.py, categories.py, transactions.py — CRUD penuh, @login_required,
hanya data milik user. Saldo wallet dihitung dari akumulasi transaksi (jangan
statis). Transaksi dukung filter month/year/category_id/q. Test tiap resource.
Uji pytest PASS, ingatkan commit.

### 3c — Budgets, Goals, Services
Fase 3c ReFinance. Buat services/budget_service.py (terpakai per kategori, sisa,
status aman/hampir≥80%/lewat>100%) + api/budgets.py; api/goals.py (progress% +
estimasi setoran/bulan). Test perhitungan + edge case (target 0, deadline lewat).
Uji pytest PASS, ingatkan commit.

### 3d — Reports, Market, Erosi (fondasi fitur unggulan)
Fase 3d ReFinance. Buat: services/report_service.py (summary, by-category,
trend) + api/reports.py; services/market_service.py (kurs USD/IDR & emas dari
API .env, cache 1 jam, fallback bila gagal) + api/market.py;
services/erosion_service.py dengan hitung_erosi(jumlah_rupiah, kurs_awal,
kurs_sekarang) -> {nilai_usd_awal, nilai_usd_sekarang, erosi_persen} sesuai
docs/04-fitur-erosi-nilai.md. Lalu di api/transactions.py: saat POST income
simpan kurs tanggal transaksi ke usd_rate_at_date (dari market_service); saat
GET income sertakan objek erosi (pakai kurs sekarang). Test: report akurat,
market di-mock (termasuk API gagal->fallback), test_erosion.py verifikasi
contoh 15.000->16.000 = -6,25% (skenario naik/turun/datar). Menutup Fase 3.
Ingatkan commit.

---

## FASE 4 — Frontend (pecah 4 sesi)

### 4a — Fondasi
Fase 4a ReFinance. Acuan docs/03-frontend-pages.md + desain docs/stitch/. Buat
base.html (navbar/sidebar + toggle dark mode), static/css/style.css dengan CSS
variables light & dark persis CLAUDE.md + font Manrope, static/js/main.js
(toggle tema set data-theme di <html>). Responsive (sidebar->hamburger di
mobile). Uji render halaman kosong, cek light/dark/mobile. Ingatkan commit.

### 4b — Auth + Dashboard
Fase 4b ReFinance. Buat views+template Login, Register, Dashboard (kartu saldo,
income/expense, progress budget, daftar goal, grafik mingguan via charts.js).
Data dummy boleh. Uji tampil+responsive+dark. Ingatkan commit.

### 4c — Transaksi, Kategori, Budget
Fase 4c ReFinance. Buat halaman Transaksi (daftar+filter+search+aksi), form
Tambah/Edit (modal), Kategori, Budget (progress bar warna aman/hampir/lewat).
Di daftar transaksi siapkan elemen badge/tooltip hover untuk pemasukan (diisi
data erosi di Fase 5). Data dummy boleh. Uji & commit.

### 4d — Wallets, Goals, Laporan, Market, Pengaturan
Fase 4d ReFinance. Buat Wallets, Goals (progress ring+setor), Laporan
(line/pie/bar Chart.js), Market (kartu kurs & emas + pesan fallback), Pengaturan
(profil, ganti password, export CSV, toggle tema). Menutup Fase 4. Uji semua
tampil+responsive, ingatkan commit.

---

## FASE 5 — Integrasi & Uji Akhir
Kita di Fase 5 (Integrasi & Uji Akhir) ReFinance. Acuan semua docs/, terutama
00-overview.md (Definition of Done). Tugas: ganti data dummy frontend dengan
fetch ke /api nyata (handle loading & error); aktifkan auth penuh (redirect
/login bila belum login); sambungkan Chart.js ke /api/reports/* (warna ikut
tema); aktifkan export CSV; sambungkan Market ke /api/market/* dengan fallback;
aktifkan fitur erosi: tooltip hover pada pemasukan menampilkan % tergerus dari
objek erosi di API, dengan keterangan "vs USD, bukan inflasi"; bila
usd_rate_at_date kosong tampilkan "data kurs tidak tersedia" tanpa crash.
Pastikan saldo wallet & total dashboard konsisten. Uji menyeluruh: T-01
transaksi valid (saldo berubah), T-02 nominal kosong (validasi), T-03 budget
lewat (peringatan), T-04 API kurs gagal (fallback), hover erosi tampil benar,
alur penuh register->login->catat->dashboard->laporan->export mulus, pytest
seluruhnya PASS. Setelah DoD terpenuhi, ringkas status & ingatkan commit.
MVP selesai.
