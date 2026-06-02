# TAHAPAN PENGERJAAN ReFinance (urutan lengkap)

Alur: desain dulu (Stitch) → siapkan konteks → coding bertahap (Claude Code,
bottom-up) → uji & commit tiap fase.

## Tahap 0 — Desain (Google Stitch)
- Buka `docs/stitch/prompt-stitch.md`.
- Kerjakan 11 prompt per halaman, beberapa per hari (jangan sekaligus).
- Ekspor tiap halaman (HTML/Figma), simpan ke `docs/stitch/`.

## Tahap 1 — Siapkan Proyek
- Buat folder `refinance/`, taruh `CLAUDE.md` di root + folder `docs/` di dalamnya.
- Buka Claude Code di folder itu. Siapkan virtualenv Python.

## Tahap 2 — Coding Bertahap (Claude Code)
Buka `docs/prompts/prompt-claude-code-semua-fase.md`, jalankan urut, satu fase
satu sesi baru:

| Urutan | Sesi | Hasil |
|--------|------|-------|
| 1 | Fase 1 Setup | struktur, factory, /ping |
| 2 | Fase 2 Database | model + migrasi + test (incl. kolom kurs) |
| 3 | Fase 3a | Auth API |
| 4 | Fase 3b | Wallets/Categories/Transactions API |
| 5 | Fase 3c | Budgets/Goals + services |
| 6 | Fase 3d | Reports/Market/**Erosi** + test |
| 7 | Fase 4a | base layout + sistem desain |
| 8 | Fase 4b | Auth + Dashboard |
| 9 | Fase 4c | Transaksi/Kategori/Budget (siapkan elemen hover) |
| 10 | Fase 4d | Wallets/Goals/Laporan/Market/Pengaturan |
| 11 | Fase 5 | Integrasi penuh + aktivasi hover erosi + uji akhir |

## Aturan Tiap Fase
1. Uji (pytest + manual happy path + kasus gagal).
2. Penuhi Definition of Done (`docs/00-overview.md`).
3. Commit Git (mis. `feat(fase-3d): erosi + market`).
4. Baru lanjut fase berikutnya. Mulai sesi Claude Code baru tiap ganti fase.

## Di Mana Fitur Erosi Dikerjakan
- Fase 2: kolom `usd_rate_at_date` di Transaction.
- Fase 3d: erosion_service + market_service + erosi di API transaksi + test.
- Fase 4c: siapkan elemen badge/tooltip hover (kosong dulu).
- Fase 5: isi tooltip dengan data nyata + fallback "data kurs tidak tersedia".

## Tips Vibe Coding Sehat
- Satu fase kecil yang bisa diuji, bukan minta seluruh app sekaligus.
- Tinjau kode agar paham, jangan terima mentah.
- Commit tiap fase berhasil — mudah mundur bila ada masalah.
