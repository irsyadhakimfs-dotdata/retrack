# 00 — Overview Proyek ReFinance

Peta proyek: fitur, halaman, struktur folder, fase, dan Definition of Done.

## Fitur MVP
| No | Fitur | Status |
|----|-------|--------|
| 1 | Dashboard Keuangan Utama | Inti |
| 2 | Pencatatan Transaksi (CRUD) | Inti |
| 3 | Kategori Pemasukan & Pengeluaran | Inti |
| 4 | Budget Bulanan per Kategori | Inti |
| 5 | Multiple Wallets / Rekening | Inti |
| 6 | Savings Goals | Inti |
| 7 | Laporan & Grafik | Inti |
| 8 | Pemantauan Kurs USD/IDR | Pendukung (API eksternal) |
| 9 | Pemantauan Harga Emas | Pendukung (API eksternal) |
| 10 | Export Data CSV | Pendukung |
| 11 | **Erosi Nilai (hover % tergerus kurs)** | **MVP — terjalin di Fase 2-5** |

## Daftar Halaman (11)
| No | Halaman | Route |
|----|---------|-------|
| 1 | Login | `/login` |
| 2 | Register | `/register` |
| 3 | Dashboard | `/` atau `/dashboard` |
| 4 | Transaksi | `/transactions` |
| 5 | Tambah/Edit Transaksi | `/transactions/new`, `/transactions/<id>/edit` |
| 6 | Kategori | `/categories` |
| 7 | Budget | `/budgets` |
| 8 | Wallets | `/wallets` |
| 9 | Savings Goals | `/goals` |
| 10 | Laporan | `/reports` |
| 11 | Market (Kurs & Emas) | `/market` |
| (+) | Pengaturan | `/settings` |

## Struktur Folder
```
refinance/
├── app/
│   ├── __init__.py        # create_app (application factory)
│   ├── config.py          # Dev/Test/Prod
│   ├── extensions.py      # db, migrate, login_manager
│   ├── models/            # DATABASE: user wallet category transaction budget goal
│   ├── api/               # API JSON: auth transactions categories wallets budgets goals reports market export
│   ├── services/          # LOGIKA: report_service budget_service market_service erosion_service
│   ├── views/             # FRONTEND: render template
│   ├── templates/         # base.html + per halaman
│   └── static/            # css/ js/ img/
├── migrations/
├── tests/                 # conftest.py + test per lapisan
├── docs/                  # dokumentasi + prompt fase
├── CLAUDE.md
├── requirements.txt
├── .env  .env.example  .gitignore
├── run.py
└── README.md
```

## Lima Fase
| Fase | Nama | Uji Berhasil Jika |
|------|------|-------------------|
| 1 | Setup | `flask run` jalan; `/ping` return OK tanpa error |
| 2 | Database | Migrasi sukses; tabel terbentuk; test_models lulus |
| 3 | API Backend | Endpoint return JSON benar; test API lulus (incl. erosi) |
| 4 | Frontend | Semua halaman tampil benar & responsive |
| 5 | Integrasi & Uji Akhir | Alur penuh + hover erosi jalan; semua test lulus; DoD terpenuhi |

## Definition of Done (per fase)
- Semua acceptance criteria fitur fase terpenuhi.
- Tidak ada error di console browser maupun terminal server.
- `pytest` fase tersebut PASS seluruhnya.
- Happy path manual berjalan.
- Kasus gagal (input kosong, data invalid, API down) tidak bikin crash.
- Sudah di-commit ke Git (mis. `feat(fase-3d): erosi nilai + market`).
