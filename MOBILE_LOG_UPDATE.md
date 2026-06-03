# MOBILE_LOG_UPDATE.md — Progres Optimasi UI/UX Mobile Vertical

> **Tujuan dokumen.** Catatan progres khusus pekerjaan **menyesuaikan UI/UX
> ReTrack agar cocok untuk mobile vertical (ponsel, portrait)**. Dokumen ini
> akan jadi acuan saat aplikasi di-deploy ke **Vercel** (web) atau di-port ke
> **Flutter** (mobile native). Untuk saat ini fokusnya **hanya** membuat
> tampilan web yang sudah ada terasa seperti aplikasi di layar ponsel — tanpa
> mengubah fitur, backend, API, atau model data.
>
> Format: satu blok per sesi, paling baru di atas. Label masalah:
> `[PRE-EXISTING]`, `[ENV]`, `[HYGIENE]`, `[BUG]`, `[BLOCKED]` + status
> `TERBUKA` / `SELESAI`.

---

## Sesi 2026-06-02 — Adaptasi Mobile Vertical (bottom nav, sheet, kartu)

### Ringkasan
Mengubah *app shell* desktop (sidebar 240px + topbar + grid lebar) agar terasa
seperti aplikasi native saat dibuka di ponsel (≤768px), **tanpa mengubah
tampilan desktop** (pendekatan *mobile-first responsive*, satu basis kode).
Brand & sistem desain **tidak diubah**: tetap Indigo `#6366F1` + Amber `#F59E0B`,
Plus Jakarta Sans + Space Grotesk, glassmorphism, Material Symbols. Semua CSS
baru ditaruh di `static/css/custom.css` (sesuai aturan proyek), tidak ada CSS di
luar file itu.

### Keputusan desain (dikonfirmasi user via pertanyaan di awal sesi)
1. **Navigasi mobile = Bottom tab bar + drawer.** 4 menu inti di bilah bawah
   (Beranda, Transaksi, Anggaran, Tabungan) + tombol **"Lainnya"** yang membuka
   drawer (sidebar lama) berisi menu lengkap (Dompet, Kategori, Laporan,
   Kurs & Emas, Investasi Emas, Pengaturan).
2. **Layar besar = Responsif penuh.** Desktop tetap seperti sekarang; hanya
   mobile yang mendapat layout vertikal baru.
3. **Pola komponen app-like:** Tabel → kartu bertumpuk; Modal → bottom sheet;
   Filter → bottom sheet.
4. **Catatan implementasi:** *safe-area* (notch/home-indicator), target sentuh
   ≥44px, dan input ≥16px (anti auto-zoom iOS) **ikut diterapkan** karena bilah
   bawah & sheet butuh itu agar tidak ketimpa gesture-bar di ponsel modern —
   walau tidak dipilih terpisah, ini bagian wajib agar pola yang dipilih bekerja.

### File dibuat / diubah

| File | Aksi | Catatan |
|---|---|---|
| `app/static/css/custom.css` | UBAH | **Inti pekerjaan.** Tambah section "18. MOBILE VERTICAL" (≤768px): bottom-nav + safe-area, padding bawah konten, modal→bottom-sheet, tabel→kartu (via `data-label`), filter→sheet, target sentuh ≥44px, input 16px, `touch-action`, `overscroll-behavior`, kolaps grid `!important`. |
| `app/templates/partials/_bottomnav.html` | BARU | Komponen bottom navigation. Tampil hanya ≤768px (CSS). Highlight aktif via `request.endpoint`/`request.blueprint`; "Lainnya" aktif bila halaman bukan salah satu menu inti; tombol "Lainnya" memanggil `toggleSidebar()` (drawer). |
| `app/templates/base.html` | UBAH | `viewport` + `viewport-fit=cover` (dukung safe-area); `{% include 'partials/_bottomnav.html' %}` di dalam `.app-layout`. |
| `app/templates/transactions/index.html` | UBAH | `data-label` pada tiap `<td>` (untuk tabel→kartu); filter bar dibungkus Alpine (`x-data`/`x-effect`) → tombol "Filter" membuka bottom sheet berisi kontrol yang **sama** (DOM tunggal, JS lama tak diubah). |
| `app/templates/gold/index.html` | UBAH | `data-label` pada tiap `<td>` tabel kepemilikan emas. |
| `app/templates/reports/index.html` | UBAH | `data-label` pada tiap `<td>` tabel kategori. |
| `app/templates/settings/index.html` | UBAH | Grid `1fr 1fr` inline → kelas `.grid-2` agar runtuh ke 1 kolom di mobile. |
| `app/templates/dwh/dashboard.html` | UBAH | Sama: grid `1fr 1fr` inline → `.grid-2`. |

> Catatan: `dashboard.html` punya grid inline `3fr 2fr` (baris Tren + Anggaran).
> Inline style mengalahkan media query biasa, jadi dipakai aturan
> `.grid-2/.grid-3/.grid-4 { grid-template-columns: 1fr !important; }` di
> `custom.css` (stylesheet `!important` menang atas inline tanpa `!important`).

### Detail teknis tiap pola

- **Bottom navigation** — `position:fixed; bottom:0`, `grid` 5 kolom, glass +
  blur, `padding-bottom: env(safe-area-inset-bottom)`. Item aktif: warna brand,
  ikon Material *filled* (`font-variation-settings:'FILL' 1`), bar indikator
  kecil di tepi atas. `.main-content` diberi `padding-bottom` = tinggi nav +
  safe-area agar konten tak tertutup. Disembunyikan di desktop (`display:none`).
- **Tabel → kartu** — generik untuk SEMUA `.table-wrap table`: di ≤768px,
  `table/tr/td` jadi `display:block`, `thead` disembunyikan, tiap baris jadi
  kartu, dan label kolom muncul lewat `td::before { content: attr(data-label) }`
  (label kiri *absolute*, nilai kanan). Baris status `colspan` (loading/kosong)
  ditangani khusus. **Wajib**: render JS tiap tabel memasang `data-label` di
  `<td>` (sudah dilakukan untuk transaksi, emas, laporan).
- **Modal → bottom sheet** — global untuk semua `.modal-overlay`/`.modal`:
  overlay `align-items:flex-end`, modal lebar penuh, sudut atas membulat,
  `transform: translateY(100%)` → `translateY(0)` saat `.open` (animasi slide),
  grip kecil di header, footer tombol ditumpuk lebar penuh, `padding-bottom`
  safe-area. Berlaku otomatis di 6 halaman bermodal (transaksi, kategori,
  anggaran, dompet, goal ×2, emas).
- **Filter → sheet** (khusus Transaksi) — search tetap terlihat; tombol "Filter"
  (mobile) membuka *bottom sheet* berisi dropdown bulan/kategori/tipe + tombol
  "Terapkan". Sheet = elemen `.filter-advanced` yang sama dengan kontrol inline
  desktop (DOM tunggal) — di-*reposition* jadi fixed sheet via CSS, di-toggle
  Alpine; `x-effect` mengunci scroll body saat sheet terbuka.
- **Sentuh & input** — `.btn`/`.btn-icon`/`.nav-item`/`.modal-close` ≥44px;
  `.form-control` `font-size:16px` (cegah auto-zoom iOS) + tinggi ≥46px;
  `touch-action: manipulation` (hilangkan delay 300ms); `overscroll-behavior-y:
  contain`.

### Verifikasi (bukti)
- **`pytest` penuh → 127 lulus, 0 gagal** (≈2 menit, Python 3.12 global).
  Membuktikan semua template (termasuk `base.html` + include bottom-nav baru)
  ter-*render* tanpa error Jinja di seluruh halaman yang diuji view test.
  (Catatan: flake DWH `[PRE-EXISTING]` dari sesi lalu **tidak** muncul di run
  ini; urutan test tidak diubah oleh pekerjaan mobile.)
- **Cek render terautentikasi** (test client) — bottom-nav, "Lainnya",
  `viewport-fit=cover`, dan struktur `filter-advanced` muncul di
  `/dashboard`, `/transactions`, `/gold`; logika aktif benar (Transaksi aktif di
  `/transactions`; "Lainnya" aktif di `/gold`). `/settings` 200 dengan `.grid-2`.
- **QA visual (Chrome headless, lebar mobile)** — dirender 2 *harness* yang
  me-*link* `style.css` + `custom.css` asli:
  1. Halaman transaksi: bottom-nav (ikon + label, "Beranda" aktif), tabel jadi
     kartu berlabel, tombol primary lebar penuh, filter satu baris. **Tidak ada
     overflow horizontal** (`scrollWidth == clientWidth`).
  2. Modal: tampil sebagai bottom sheet (grip, scrim, footer tombol ditumpuk,
     "Simpan" menonjol).
  - *Catatan QA:* Chrome headless di Windows ini mengunci *layout viewport* ke
    ~472px apa pun `--window-size`-nya, jadi screenshot 390px sempat ter-*clip*
    di kanan (artefak kamera, **bukan** bug layout — sudah dipastikan via
    `scrollWidth==clientWidth`). Tangkapan final diambil pada lebar 472px.

### Yang TIDAK diubah (sesuai instruksi "fokus mobile saja")
- Fitur, endpoint API, *service*, model, migrasi — **nihil perubahan**.
- Tampilan **desktop** — tidak berubah (semua aturan baru di `@media
  (max-width:768px)`, kecuali util `.bottom-nav{display:none}` & `touch-action`).
- Brand/warna/font/`tailwind.config` — tidak diubah.
- Landing page (`landing.html`) — di luar lingkup; tetap seperti sesi lalu.

### Masalah ditemukan / catatan

#### #1 — `[PRE-EXISTING]` Flake isolasi test DWH — **TERBUKA (warisan)**
Tidak muncul di run ini, tapi belum diperbaiki di akar (lihat `LOG_UPDATE.md`
sesi landing, Masalah #1). Tidak terkait pekerjaan mobile.

#### #2 — `[HYGIENE]` Bottom-nav memilih 4 menu inti — **SELESAI (keputusan)**
Beranda / Transaksi / Anggaran / Tabungan dipilih sebagai "kebiasaan uang"
harian. Sisanya (Dompet, Kategori, Laporan, Kurs & Emas, Investasi Emas,
Pengaturan) lewat "Lainnya". Bila prioritas menu berubah, edit
`partials/_bottomnav.html` (dan logika `_is_primary`).

### Langkah selanjutnya (TODO terbawa)
- [ ] **User: QA visual di perangkat nyata** — ponsel kecil (375px) & besar,
      mode terang + gelap: bottom-nav, drawer "Lainnya", tabel-kartu di
      Transaksi/Emas/Laporan, modal-sheet (tambah transaksi/budget/goal/emas),
      filter-sheet di Transaksi, area aman (notch/home-indicator).
- [ ] **Deploy Vercel** — perubahan murni front-end (template/CSS/JS); aset
      `static/*` dilayani Flask juga di Vercel (lihat `next_step.md` 1.2).
      Preview dulu, production menunggu konfirmasi user.
- [ ] **Acuan port Flutter** — peta padanan: bottom-nav → `BottomNavigationBar`/
      `NavigationBar`; drawer "Lainnya" → `Drawer`/`endDrawer`; modal-sheet →
      `showModalBottomSheet`; tabel-kartu → `ListView` + `Card`; filter-sheet →
      `showModalBottomSheet`. Token warna/spacing ada di `custom.css` `:root`.
- [ ] (Opsional) Pertimbangkan FAB "+" untuk tambah transaksi cepat (sempat jadi
      opsi navigasi; belum dipilih).
- [ ] (Opsional, warisan) Perbaiki isolasi test DWH (#1) & sinkronkan brand di
      `CLAUDE.md` (masih tertulis teal/pink/Manrope — sudah usang).

### Cara menjalankan & menguji (terbukti jalan sesi ini)
```powershell
Set-Location "D:\VS CODE\CLAUDE\ReTrack_1.3_Mobile"
python -m pytest -q                 # suite penuh → 127 passed
python run.py                       # atau: flask run  (dev server)
```
QA mobile cepat di browser desktop: buka DevTools → *device toolbar* (Ctrl+Shift+M)
→ pilih lebar ≤768px (mis. iPhone SE 375px) untuk melihat bottom-nav,
tabel-kartu, modal-sheet, dan filter-sheet aktif.

---

*Dibuat pada sesi 2026-06-02 (optimasi UI/UX mobile vertical). Tambahkan blok
sesi baru di ATAS entri ini saat ada update mobile berikutnya.*
