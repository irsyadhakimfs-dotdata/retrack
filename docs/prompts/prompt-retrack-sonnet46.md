# Prompt Coding — ReTrack (4 Perubahan) untuk Claude Sonnet 4.6

> **Cara pakai:** Buka sesi **baru** Claude Code dengan model **Sonnet 4.6** di
> folder proyek. Copy-paste blok di bawah garis sebagai pesan pertama. Prompt ini
> self-contained dan **plan-first**: Sonnet wajib membuat rencana & minta
> persetujuan sebelum menulis kode tiap perubahan.

---

## PROMPT (copy mulai dari sini)

Kamu mengerjakan proyek **ReTrack** (dulu "ReFinance"), web personal finance &
budget planner Flask untuk pengguna Indonesia. Tugasmu menjalankan **4 perubahan**
yang dispesifikasikan di `docs/05-perubahan-retrack.md`. Ikuti instruksi ini
dengan disiplin — aku akan meninjau tiap langkah.

### 0. Baca & pahami dulu (WAJIB sebelum apa pun)
Baca berkas ini lengkap, jangan diasumsikan:
- `CLAUDE.md` — aturan pengembangan, stack, palet warna light/dark.
- `docs/00-overview.md` — fitur, halaman, **Definition of Done**.
- `docs/05-perubahan-retrack.md` — **spesifikasi 4 perubahan + 3 keputusan yang
  sudah disepakati** (sumber kebenaran tugas ini).
- `docs/03-frontend-pages.md` — komponen halaman Market & aturan Chart.js.
Lalu lihat kode aktual yang akan disentuh:
- `app/services/market_service.py`, `app/api/market.py`,
  `app/templates/market/index.html`, `app/static/js/charts.js`,
  `tests/test_api_3d.py`, `app/templates/base.html`.

### 1. Aturan main (TIDAK BOLEH dilanggar)
- Pertahankan application factory & **pemisahan lapisan tegas**: `models/` (data),
  `api/` (selalu JSON `{ok,data}`/`{ok,error}`), `services/` (logika bisnis murni),
  `views/` (render template).
- Komentar Python pakai `#` **Bahasa Indonesia** jelas (untuk pemula). Semua teks
  UI Bahasa Indonesia. Jangan hardcode secret/interval — pakai `.env` + `config.py`.
- Warna lewat **CSS variables**; chart ambil warna via `getComputedStyle` agar
  ikut `data-theme`.
- **Tulis/perbarui test untuk setiap perubahan perilaku.** Jangan biarkan test
  lama rusak diam-diam.
- **Jangan refactor di luar scope** perubahan yang sedang dikerjakan.

### 2. Cara kerja: PLAN-FIRST, satu perubahan satu siklus
Untuk **setiap** perubahan, ikuti siklus ini dan **berhenti menunggu approval-ku**:
1. Sampaikan **rencana langkah teknis** (file mana disentuh, apa berubah, test apa).
2. Tunggu aku bilang "lanjut".
3. Implementasi.
4. Jalankan `pytest -q` + jelaskan cara uji manual.
5. Laporkan hasil, **ingatkan aku commit** dengan pesan yang sudah ditentukan.
   **Jangan commit sendiri** kecuali kuminta.
6. Baru lanjut ke perubahan berikutnya.

Kerjakan **berurutan: 1 → 2 → 3 → 4**. Jangan gabung commit.

### 3. Tiga keputusan yang sudah final (jangan tawar ulang)
1. **Sumber data market = yfinance.** Tabel `RateHistory`, APScheduler, dan seed
   dummy **DIBATALKAN**. yfinance menyediakan data historis langsung.
2. **Rename hanya nama tampilan.** Nama teknis `refinance` (folder package,
   `refinance.db`, import) **tetap** — jangan rename, supaya import/migrasi aman.
3. Commit per perubahan.

### 4. Ringkas tiap perubahan (detail penuh di `docs/05`)

**Perubahan 1 — Rename tampilan ReFinance → ReTrack.**
Grep `refinance` di seluruh proyek, ganti **hanya yang terlihat user** (title,
navbar, login, footer, README judul, teks UI). Biarkan nama teknis. Pastikan
`flask run` & `pytest` tetap hijau.
→ Commit: `refactor: rename tampilan ReFinance menjadi ReTrack`

**Perubahan 2 — Logo ReTrack + favicon.**
File sumber `Logo_ReTrack.png` (800×800, hitam di latar putih solid). Simpan ke
`app/static/img/`, buat turunan `logo-32.png` & `logo-192.png` (boleh skrip Pillow
sekali jalan), referensikan favicon + logo di `base.html` & halaman login.
**Tangani dark mode** (logo hitam-latar-putih jelek di bg gelap): pakai Solusi A
(2 varian transparan light/dark, tukar via `data-theme`) bila sempat, atau
Solusi B (chip putih) bila mepet. Tanyakan ke aku bila file `Logo_ReTrack.png`
belum ada di proyek.
→ Commit: `feat: pasang logo ReTrack baru + favicon`

**Perubahan 3 — Market via yfinance + linechart kurs 6 bulan.** (pecah 3a→3d)
- 3a: `pip install yfinance`, tambah ke `requirements.txt` (tanpa API key).
- 3b: Refactor `services/market_service.py` ke yfinance. Ticker USD/IDR = `IDR=X`,
  emas = `GC=F`. **Pertahankan bentuk return lama**: `get_usd_idr()` →
  `{"rate",...}`, `get_gold()` → `{"price_idr",...}`, supaya erosi & dashboard
  tak ikut berubah. Tambah `get_usd_idr_history(months=6)` → list
  `[{"date","rate"}]` urut naik. Pertahankan **cache 1 jam + fallback** +
  `reset_cache()`. Bungkus yfinance dengan `try/except`, jangan bocorkan exception.
- 3c: Tambah `GET /api/market/usd-idr/history?months=6` di `app/api/market.py`;
  pertahankan endpoint terkini & gold. **WAJIB perbaiki `tests/test_api_3d.py`**:
  test lama mem-`patch app.services.market_service.requests.get` yang kini tidak
  ada lagi — ganti jadi `patch` pemanggilan yfinance (mis.
  `app.services.market_service.yf.Ticker`) untuk skenario normal/fallback/history.
  Tambah test endpoint history. **Test tidak boleh memanggil internet nyata.**
- 3d: Halaman Market (`templates/market/index.html` + `static/js/charts.js`) →
  line chart Chart.js 6 bulan (warna dari CSS variable). Auto-refresh klien pakai
  `setInterval` tiap `MARKET_REFRESH_HOURS` (dari `.env`/`config.py`, default 6;
  boleh perpendek untuk demo). Tangani data <2 titik & yfinance down tanpa crash.
→ Commit: `feat(market): pindah ke yfinance + linechart kurs 6 bulan auto-update`

**Perubahan 4 — "Sesuaikan web agar sesuai project".**
Masih ambigu. **JANGAN kerjakan apa pun** — tanya aku dulu maksud spesifiknya
(branding penuh? penyesuaian fitur tracker? rapikan struktur?). Tunggu jawabanku.

### 5. Definition of Done (cek tiap perubahan sebelum lapor selesai)
- Acceptance criteria di `docs/05` terpenuhi.
- Tidak ada error di console browser maupun terminal server.
- `pytest` PASS seluruhnya (termasuk test market yang diperbarui).
- Happy path manual jalan; kasus gagal (yfinance down, data kosong) tidak crash.
- Sudah kuminta commit (jangan commit otomatis).

### 6. Mulai sekarang
Mulai dengan **Perubahan 1**: tampilkan dulu hasil grep `refinance` (pisahkan
"nama tampilan" vs "nama teknis") + rencana edit, lalu **tunggu approval-ku**.

### Referensi perintah
```bash
flask run
pytest -q
pytest tests/test_api_3d.py     # market (setelah mock diperbarui)
pip install yfinance
```

(akhir prompt)
