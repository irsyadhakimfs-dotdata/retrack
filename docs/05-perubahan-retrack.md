# 05 — Perubahan: ReFinance → ReTrack

> **Cara pakai file ini di Claude Code:**
> Buka proyek di terminal, jalankan `claude`, lalu ketik:
> *"Baca `CLAUDE.md`, `docs/00-overview.md`, dan `docs/05-perubahan-retrack.md`.
> Buatkan rencana bertahap (planning) untuk 4 perubahan di dokumen 05 SEBELUM
> menulis kode apa pun. Tunggu persetujuanku tiap fase."*
>
> File ini adalah **spesifikasi perubahan**, bukan perintah eksekusi langsung.
> Biarkan Claude Code yang menyusun langkah teknis karena ia bisa membaca kode
> aktual proyek (yang dokumen ini tidak punya).

Ada 4 perubahan. Kerjakan **berurutan**, commit per perubahan, jangan gabung.
Patuhi semua aturan di `CLAUDE.md` (pemisahan lapisan, test per fitur,
komentar `#` Bahasa Indonesia, UI Bahasa Indonesia).

---

## Keputusan yang sudah disepakati (baca dulu)

Tiga keputusan ini mengikat dan sudah mengubah isi dokumen di bawah:

1. **Sumber data market = yfinance (Yahoo Finance).** Perubahan 3 TIDAK lagi
   memakai pendekatan "nabung kurs harian ke DB sendiri + scheduler + seed
   dummy". yfinance menyediakan data **historis langsung**, jadi tabel
   `RateHistory`, APScheduler, dan skrip seed **dibatalkan**. yfinance menjadi
   satu-satunya sumber untuk kurs terkini USD/IDR, harga emas, dan riwayat 6 bulan.
2. **Rename hanya nama tampilan.** Pada Perubahan 1, ganti hanya yang terlihat
   user (title, navbar, login, footer, README, teks UI). **Nama teknis tetap
   `refinance`** (folder package, `refinance.db`, import path) agar tidak
   memecah import & path migrasi.
3. **Urutan & commit per perubahan tetap berlaku.**

---

## Perubahan 1 — Rename produk: ReFinance → ReTrack

**Tujuan:** semua kemunculan nama lama yang **terlihat user** jadi "ReTrack".

**Langkah investigasi dulu (jangan asal replace):**
1. Cari semua kemunculan string lama:
   ```bash
   grep -rni "refinance" . --include="*.py" --include="*.html" \
     --include="*.js" --include="*.css" --include="*.md" --include="*.txt"
   ```
2. Bedakan dua hal:
   - **Nama tampilan** (judul `<title>`, navbar, footer, README, teks UI) →
     ganti jadi `ReTrack`.
   - **Nama teknis** (folder package `refinance/`, nama database `refinance.db`,
     import path, nama app di `create_app`) → **BIARKAN tetap `refinance`**
     sesuai keputusan di atas. Jangan rename folder/package.

**Acceptance:**
- Tidak ada lagi tulisan "ReFinance" yang terlihat user (browser tab, navbar,
  halaman login, footer, README judul).
- Nama teknis `refinance` boleh tetap ada di kode/DB/import.
- Aplikasi tetap `flask run` tanpa error.
- `pytest` tetap lulus.

**Commit:** `refactor: rename tampilan ReFinance menjadi ReTrack`

---

## Perubahan 2 — Pasang logo ReTrack baru

**Berkas logo:** `Logo_ReTrack.png` (800×800 px, RGB, **latar putih solid /
tidak transparan**, gambar hitam).

**Langkah:**
1. Simpan file ke `app/static/img/logo.png` (timpa logo lama bila ada; kalau
   nama lama beda, sesuaikan referensinya di template).
2. **Buat 2 ukuran turunan** supaya halaman ringan (jangan render 800px langsung
   di navbar). Bisa pakai Pillow di skrip sekali-jalan atau tool gambar:
   - `logo-32.png` (favicon / navbar kecil)
   - `logo-192.png` (header, halaman login)
   Tambahkan juga `favicon.ico` kalau mau rapi.
3. Referensikan di `base.html`:
   ```html
   <link rel="icon" href="{{ url_for('static', filename='img/logo-32.png') }}">
   <img src="{{ url_for('static', filename='img/logo-192.png') }}"
        alt="ReTrack" class="app-logo">
   ```

**PENTING — masalah dark mode:**
Logo ini **hitam di atas latar putih solid**. Di dark mode (bg `#020617`)
kotak putihnya akan terlihat mencolok dan jelek. Pilih salah satu solusi dan
laksanakan:
- **Solusi A (paling rapi):** siapkan **2 varian transparan** — `logo-light.png`
  (gambar hitam, background dihapus jadi alpha) untuk light mode, dan
  `logo-dark.png` (gambar putih, transparan) untuk dark mode — lalu tukar via
  atribut `data-theme` (CSS `content`/`src` atau dua `<img>` yang di-toggle).
- **Solusi B (kompromi cepat):** taruh logo di dalam "chip" berlatar putih
  dengan border-radius di kedua tema. Tanpa edit gambar, tapi kurang menyatu.

Rekomendasi: **Solusi A** kalau punya waktu, **Solusi B** kalau mepet deadline.

**Acceptance:**
- Favicon muncul di tab browser.
- Logo tampil benar & tidak pecah di navbar + halaman login.
- Logo tetap enak dilihat di **light maupun dark mode**.

**Commit:** `feat: pasang logo ReTrack baru + favicon`

---

## Perubahan 3 — Market via yfinance + kurs USD/IDR linechart 6 bulan

**Konteks masalah & solusi:**
API kurs lama (`open.er-api.com`) hanya menyediakan kurs **terkini**, tidak ada
data historis — itulah kenapa chart 6 bulan dulu dianggap sulit. **yfinance
(Yahoo Finance) menyelesaikan ini**: ia menyediakan data historis langsung,
tanpa API key. Jadi kita **ganti seluruh sumber data market ke yfinance** dan
tidak perlu menyimpan riwayat sendiri.

Ticker yang dipakai:
- USD/IDR → `IDR=X`
- Emas → `GC=F` (gold futures, USD per troy ounce)

### 3a. Dependency
- `pip install yfinance`, lalu tambahkan ke `requirements.txt`.
- yfinance menarik `pandas` & `requests` sebagai dependency — biarkan terpasang.
- Tidak perlu API key. (Boleh hapus `EXCHANGE_API_KEY` dari `.env.example` bila
  tak terpakai lagi.)

### 3b. Refactor `services/market_service.py` ke yfinance
Pertahankan **bentuk return yang sama** agar fitur lain (erosi, transaksi,
dashboard) tidak ikut berubah:
- `get_usd_idr()` → kurs terkini = harga `Close` terakhir `IDR=X`. Tetap
  kembalikan `{"rate": float, "source": ..., "cached": bool}`.
- `get_gold()` → `Close` terakhir `GC=F` (USD/oz) × kurs USD/IDR = IDR/oz. Tetap
  kembalikan `{"price_idr": int, "source": ..., "cached": bool}`.
- **`get_usd_idr_history(months=6)` (baru)** → `yf.Ticker("IDR=X").history(
  period="6mo")`, kembalikan list `[{"date": "YYYY-MM-DD", "rate": float}, ...]`
  urut tanggal naik. Ini sumber data linechart.
- Pertahankan **cache 1 jam** + **fallback** ke cache terakhir bila yfinance
  gagal (offline / rate-limit / kosong). Pertahankan `reset_cache()`.
- yfinance bisa lambat/flaky → bungkus dengan `try/except`, `timeout` wajar,
  dan jangan biarkan exception bocor ke endpoint.

### 3c. Endpoint API (`app/api/market.py`)
- Tambah `GET /api/market/usd-idr/history?months=6` →
  `{"ok": true, "data": [{"date","rate"}, ...]}`.
- Pertahankan `GET /api/market/usd-idr` (terkini) & `GET /api/market/gold`.
- **PENTING — perbaiki test lama:** `tests/test_api_3d.py` saat ini mem-`patch`
  `app.services.market_service.requests.get`. Karena sumber pindah ke yfinance,
  mock itu **akan rusak**. Update test agar mem-`patch` pemanggilan yfinance
  (mis. `app.services.market_service.yf.Ticker`) untuk skenario: data normal,
  fallback saat exception, dan history. Tambah test untuk endpoint history baru.

### 3d. Frontend: halaman Market jadi linechart
- Ganti kartu angka kurs statis → **line chart Chart.js** 6 bulan (X = tanggal,
  Y = kurs USD/IDR). Boleh tetap tampilkan angka kurs terkini sebagai label di
  atas chart. Kartu emas tetap (angka), datanya kini dari yfinance.
- Konfigurasi chart di `static/js/charts.js`; ambil warna dari CSS variable via
  `getComputedStyle` agar selaras light/dark (konsisten `03-frontend-pages.md`).
- **Auto-refresh sisi klien (data stream):** `setInterval` fetch ulang endpoint
  history tiap **X jam**. Interval diatur lewat `.env`/`config.py` (mis.
  `MARKET_REFRESH_HOURS`, default 6), **jangan hardcode**; untuk demo boleh
  perpendek. Istilah konsisten: "data stream update tiap X jam".
- Tangani data kosong/sedikit dengan anggun (pesan "riwayat kurs belum tersedia"
  bila titik < 2), jangan crash. Tampilkan pesan fallback bila yfinance down.

**Acceptance:**
- `yfinance` ada di `requirements.txt`, `market_service` memakainya.
- `GET /api/market/usd-idr/history?months=6` return JSON benar; test API lulus.
- `get_usd_idr()` & `get_gold()` tetap kembalikan bentuk lama; erosi & dashboard
  tetap jalan.
- Halaman Market menampilkan line chart 6 bulan **data nyata** yang menyegarkan
  diri otomatis tiap X jam.
- Tidak crash saat data kosong / yfinance down (pakai fallback cache).
- Warna chart mengikuti light/dark mode.
- `pytest` (termasuk `test_api_3d.py` yang sudah diperbarui) lulus seluruhnya.

**Commit (boleh dipecah per sub-fase):**
`feat(market): pindah ke yfinance + linechart kurs 6 bulan auto-update`

---

## Perubahan 4 — "Menyesuaikan web Flask agar sesuai project"

Permintaan ini masih umum. Sebelum eksekusi, Claude Code **wajib tanya saya**
maksud spesifiknya. Kemungkinan yang dimaksud:
- Menyamakan branding penuh ke ReTrack (warna, tone, copy) — sebagian sudah
  tercakup Perubahan 1 & 2.
- Menyesuaikan fitur agar pas dengan tujuan "tracker" (bukan sekadar finance).
- Merapikan struktur agar 100% sesuai `00-overview.md`.

Jangan kerjakan apa pun di sini tanpa klarifikasi dari saya.

---

## Urutan kerja & aturan main
1. Perubahan 1 (rename tampilan saja) → commit.
2. Perubahan 2 (logo + favicon) → commit.
3. Perubahan 3 (yfinance + linechart), pecah jadi 3a→3d, test tiap langkah
   (termasuk perbaikan mock `test_api_3d.py`) → commit.
4. Perubahan 4 hanya setelah klarifikasi.

**Definition of Done tiap perubahan** (ikut `00-overview.md`):
- Acceptance criteria terpenuhi.
- Tidak ada error di console browser & terminal.
- `pytest` PASS.
- Happy path manual jalan.
- Sudah di-commit ke Git.
