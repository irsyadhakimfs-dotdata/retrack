# LOG_UPDATE.md — Catatan Update & Masalah ReTrack

> **Tujuan dokumen.** Catatan berjalan (running log) antar-sesi untuk merekam
> *apa yang berubah* dan *masalah apa yang ditemui* tiap sesi. Berbeda dari
> `next_step.md` (panduan tugas berikutnya), file ini fokus pada **riwayat**:
> supaya sesi mendatang bisa melihat "masalah sebelumnya" tanpa menebak.
>
> Format: satu blok per sesi, paling baru di atas. Tandai masalah dengan label
> `[PRE-EXISTING]`, `[ENV]`, `[HYGIENE]`, `[BUG]`, `[BLOCKED]`, lalu status
> `TERBUKA` / `SELESAI`.

---

## Sesi 2026-06-02 — Landing Page Publik

### Yang dikerjakan
Membuat **landing page publik** di `/` (mengikuti `next_step.md` Bagian 3),
dengan keputusan user: **nada serius-fintech profesional** + **mock cuplikan
dashboard (kartu glass)** di hero.

Metode: **TDD** (RED → GREEN). Test ditulis dulu, dilihat gagal, baru implementasi.

**File dibuat / diubah:**

| File | Aksi | Catatan |
|---|---|---|
| `app/templates/landing.html` | BARU | Halaman standalone (TIDAK extends `base.html`). Salin boilerplate `<head>` + blok `tailwind.config` indigo/amber dari `base.html`, skrip anti-FOUC tema, Alpine untuk menu mobile, `main.js` di akhir body (mengikat `.theme-toggle`). |
| `app/views/auth_views.py` | UBAH | `index()`: tamu → `render_template('landing.html')` (sebelumnya redirect `/login`); user login tetap → `/dashboard`. |
| `app/static/css/custom.css` | UBAH | Tambah blok "17. Landing page" di akhir: `[x-cloak]`, `.landing-navlink`, `.landing-gradient-text`, `.landing-blob`. Tidak ada CSS di luar `custom.css`. |
| `tests/test_landing.py` | BARU | 3 test rute landing. |

Struktur halaman: navbar glass sticky (menu mobile via Alpine) → hero (teks +
CTA + kartu preview dashboard solid) → 6 kartu fitur → band keamanan/kepercayaan
→ CTA penutup bergradien → footer. Indigo `#6366F1` + Amber `#F59E0B`,
Plus Jakarta Sans + Space Grotesk, ikon Material Symbols (tanpa emoji), copy
Bahasa Indonesia, toggle dark mode, skip-link + `alt`/heading untuk aksesibilitas.

### Status test
- `pytest tests/test_landing.py` → **3/3 LULUS**.
- `pytest` (penuh) → **126 lulus, 1 GAGAL** (lihat Masalah #1 — bukan akibat
  pekerjaan landing).

### Masalah ditemukan

#### #1 — `[PRE-EXISTING]` Kegagalan test DWH karena isolasi test — **TERBUKA**
- **Test:** `tests/test_dwh.py::TestErosiSummary::test_erosi_dihitung_bila_kurs_ada`
- **Gejala (tergantung cara dijalankan):**
  - `pytest tests/test_dwh.py` (satu file) → **11/11 lulus**.
  - test ini **sendirian** (`...::test_erosi_dihitung_bila_kurs_ada`) → GAGAL
    `assert 0 == 1` (tidak ada data; ia bergantung pada data yang dibuat
    test-test lain di kelas yang sama).
  - `pytest` penuh → GAGAL `assert 2 == 1` (`total_income_transactions`
    membengkak karena data transaksi **bocor** dari test yang jalan
    **sebelumnya**).
- **Akar masalah:** test di `TestErosiSummary` memakai fixture `client` saja,
  **bukan** fixture `db`. Di `tests/conftest.py`, pembersihan tabel
  (`for table in reversed(... ): table.delete()`) hanya jalan untuk test yang
  meminta `db`. Maka baris DB (User/Wallet/Transaction/Fact) yang dibuat lewat
  API **tidak dibersihkan** antar-test → bocor lintas test & lintas file. Test
  ini juga **saling bergantung urutan** (anti-pattern), bukan mandiri.
- **Kenapa BUKAN akibat landing page:** `test_landing.py` berurutan **setelah**
  `test_dwh.py` (alfabet: `d` < `l`) sehingga tidak mengubah state sebelum DWH;
  test landing juga **tidak membuat transaksi**; dan kode landing
  (view/template/CSS) **tidak pernah di-import** oleh test DWH.
- **Saran perbaikan (nanti):** jadikan test DWH mandiri — minta fixture `db`
  (agar tabel dibersihkan), atau tambahkan autouse cleanup global di
  `conftest.py` yang membersihkan tabel untuk **semua** test (bukan hanya yang
  memakai `db`), atau scope data per-user dan assert relatif. Jangan
  mengandalkan urutan test.

#### #2 — `[ENV]` venv `ReFinance\.venv` kosong/rusak — **TERBUKA (menunggu keputusan)**
- `D:\VS CODE\CLAUDE\ReFinance\.venv` **ada** (Python 3.12.13) tetapi **tanpa
  `pip`** dan **tanpa** Flask/flask_login/flask_sqlalchemy/flask_migrate/
  pytest/yfinance/psycopg2 → **tidak bisa** menjalankan app/test ReTrack.
- Tidak ada `.venv` di dalam `ReTrack_1.3` maupun `ReFinance-MD-Lengkap`.
- Satu-satunya interpreter yang berfungsi penuh: **Python 3.12 global**
  `C:\Users\irsya\AppData\Local\Programs\Python\Python312\python.exe`
  (inilah yang dipakai menjalankan suite di atas; suite lulus selain Masalah #1).
- Catatan: di harness ini, `activate` tidak persisten antar-perintah shell;
  pemanggilan sebaiknya langsung ke `...\python.exe`.
- **Keputusan environment ditunda** (user akan testing personal dulu). Opsi:
  (a) pakai Python global, (b) buat `.venv` baru di `ReTrack_1.3` lalu
  `pip install -r requirements-dev.txt`, (c) perbaiki `ReFinance\.venv`
  (`python -m ensurepip` lalu install requirements-dev).

#### #3 — `[HYGIENE]` Duplikat proyek/tests lintas folder — **TERBUKA**
- Ada **tiga** folder serupa di `D:\VS CODE\CLAUDE\`: `ReFinance`,
  `ReFinance-MD-Lengkap`, dan `ReTrack_1.3` (kemungkinan tahapan/evolusi proyek
  yang sama; brand di kode = "ReTrack", judul lama `CLAUDE.md` = "ReFinance",
  kunci localStorage = `refinance-theme`).
- Saat `pytest` penuh, traceback menampilkan path
  `..\ReFinance-MD-Lengkap\tests\test_dwh.py` padahal `ReTrack_1.3\tests\test_dwh.py`
  juga **ada secara fisik** dan **bukan** symlink. Terkonfirmasi salinan
  `test_dwh.py` memang **ada juga** di `ReFinance-MD-Lengkap\tests\`.
- **Risiko:** menjalankan pytest dari direktori yang salah bisa mengoleksi/
  meng-import salinan test dari proyek tetangga → hasil membingungkan & bisa
  jadi sumber polusi data lintas test. **Selalu jalankan dari**
  `D:\VS CODE\CLAUDE\ReTrack_1.3` dan pastikan tidak ada koleksi yang melebar
  keluar folder ini.

### Perubahan belum di-commit (git status saat sesi ditutup)
Branch `main` selaras dengan `origin/main` (belum ada commit baru):
```
 M .gitignore
 M app/static/css/custom.css
 M app/views/auth_views.py
?? app/templates/landing.html
?? next_step.md
?? tests/test_landing.py
```
> Catatan: `next_step.md` masih **untracked** (belum pernah di-commit).
> `LOG_UPDATE.md` (file ini) juga baru dibuat → akan muncul untracked.

### Langkah selanjutnya (TODO terbawa)
- [ ] **User: testing personal** landing page (QA visual terang & gelap, menu
      mobile Alpine, CTA → `/login` & `/register`, responsif).
- [ ] Tetapkan **environment Python** (Masalah #2).
- [ ] Commit + push perubahan landing ke `main` (lihat `next_step.md` 3.8) —
      **menunggu** hasil testing user.
- [ ] Deploy **preview** Vercel; **production** (`vercel --prod`) menunggu
      konfirmasi user.
- [ ] (Opsional) Perbaiki isolasi test DWH (Masalah #1).
- [ ] (Opsional) Sinkronkan deskripsi brand di `CLAUDE.md` (masih menulis
      teal/pink/Manrope — sudah usang; brand asli Indigo/Amber + Plus Jakarta
      Sans/Space Grotesk). Konfirmasi user dulu.

### Cara menjalankan (yang terbukti jalan sesi ini)
```powershell
Set-Location "D:\VS CODE\CLAUDE\ReTrack_1.3"
python -m pytest -q                     # suite penuh
python -m pytest tests/test_landing.py -v
python run.py                           # atau: flask run  (dev server)
```

---

*Dibuat pada sesi 2026-06-02 (implementasi landing page). Tambahkan blok sesi
baru di ATAS entri ini saat ada update berikutnya.*
