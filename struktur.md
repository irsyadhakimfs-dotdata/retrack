# Struktur Pohon Proyek ReFinance-MD-Lengkap
> Dihasilkan: 2026-06-01 | Kedalaman: 3 level | Tidak termasuk `__pycache__` & `.pytest_cache`

```
ReFinance-MD-Lengkap/
├── .env
├── .env.example
├── .gitignore
├── CLAUDE.md
├── ETLPROCESS.md
├── jawaban.md
├── keuangan_generated (1).csv
├── PROGRESS.md
├── README.md
├── requirements.txt
├── run.py
├── TAHAPAN.md
│
├── .claude/
│   └── settings.local.json
│
├── app/
│   ├── config.py
│   ├── extensions.py
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── budgets.py
│   │   ├── categories.py
│   │   ├── dwh.py
│   │   ├── export.py
│   │   ├── goals.py
│   │   ├── gold.py
│   │   ├── market.py
│   │   ├── reports.py
│   │   ├── transactions.py
│   │   ├── user.py
│   │   ├── wallets.py
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── budget.py
│   │   ├── category.py
│   │   ├── dwh.py
│   │   ├── gold_holding.py
│   │   ├── savings_goal.py
│   │   ├── transaction.py
│   │   ├── user.py
│   │   ├── wallet.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── budget_service.py
│   │   ├── erosion_service.py
│   │   ├── etl_service.py
│   │   ├── market_service.py
│   │   ├── report_service.py
│   │   └── __init__.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── custom.css
│   │   │   └── style.css
│   │   ├── img/
│   │   │   ├── logo-32.png
│   │   │   ├── logo-dark.png
│   │   │   └── logo-light.png
│   │   └── js/
│   │       ├── api.js
│   │       ├── charts.js
│   │       └── main.js
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── budgets/
│   │   │   └── index.html
│   │   ├── categories/
│   │   │   └── index.html
│   │   ├── dwh/
│   │   │   └── dashboard.html
│   │   ├── goals/
│   │   │   └── index.html
│   │   ├── gold/
│   │   │   └── index.html
│   │   ├── market/
│   │   │   └── index.html
│   │   ├── partials/
│   │   │   └── _sidebar.html
│   │   ├── reports/
│   │   │   └── index.html
│   │   ├── settings/
│   │   │   └── index.html
│   │   ├── transactions/
│   │   │   └── index.html
│   │   └── wallets/
│   │       └── index.html
│   │
│   └── views/
│       ├── auth_views.py
│       ├── budget_views.py
│       ├── category_views.py
│       ├── dashboard_views.py
│       ├── dwh_views.py
│       ├── goal_views.py
│       ├── gold_views.py
│       ├── market_views.py
│       ├── report_views.py
│       ├── settings_views.py
│       ├── transaction_views.py
│       ├── wallet_views.py
│       └── __init__.py
│
├── assets/
│   └── Logo_ReTrack.png
│
├── docs/
│   ├── 00-overview.md
│   ├── 01-database-schema.md
│   ├── 02-api-spec.md
│   ├── 03-frontend-pages.md
│   ├── 04-fitur-erosi-nilai.md
│   ├── 05-perubahan-retrack.md
│   ├── 06-perubahan4-dwh.md
│   ├── prompts/
│   │   ├── prompt-claude-code-semua-fase.md
│   │   └── prompt-retrack-sonnet46.md
│   └── stitch/
│       ├── prompt-stitch.md
│       ├── stitch-design-mcp.md
│       ├── images/
│       │   ├── budget.png
│       │   ├── daftar-akun.png
│       │   ├── dashboard.png
│       │   ├── kategori.png
│       │   ├── laporan.png
│       │   ├── login.png
│       │   ├── market.png
│       │   ├── savings-goals.png
│       │   ├── tambah-transaksi.png
│       │   ├── transaksi.png
│       │   └── wallets.png
│       └── screens/
│           ├── budget.html
│           ├── daftar-akun.html
│           ├── dashboard.html
│           ├── design-system.json
│           ├── kategori.html
│           ├── laporan.html
│           ├── login.html
│           ├── market.html
│           ├── savings-goals.html
│           ├── tambah-transaksi.html
│           ├── transaksi.html
│           └── wallets.html
│
├── dwh/
│   ├── build_docx.py
│   ├── CLAUDE (3).md
│   ├── dwh_star_schema.sql
│   ├── elaborasi.md
│   ├── Materi 4.md
│   ├── PPT-ReTrack-DWH.docx
│   ├── PPT-ReTrack-DWH.md
│   ├── PPT_Materi_3_Enterprise_Data_Data_Mart_Kualitas_Data.md
│   ├── PPT_Materi_6_Desain_Data_Warehouse.md
│   ├── PPT_Materi_7_OLTP_dan_OLAP.md
│   ├── PPT_Materi_8_Digital_Dashboard.md
│   ├── star-schema-mermaid.md
│   └── Tugas Project II Data Warehouse 2025 2026.md
│
├── instance/
│   └── refinance_dev.db
│
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       ├── 596f653d12e2_add_gold_holdings_table.py
│       ├── 8df4d27d7c4b_add_dwh_star_schema_tables.py
│       ├── 942b014373ce_inisialisasi_semua_model_fase_2.py
│       └── a1c2f3e4b5d6_transaction_date_to_datetime.py
│
├── scripts/
│   └── import_keuangan_csv.py
│
└── tests/
    ├── conftest.py
    ├── test_api_3b.py
    ├── test_api_3c.py
    ├── test_api_3d.py
    ├── test_auth.py
    ├── test_dwh.py
    ├── test_erosion.py
    ├── test_fase5.py
    ├── test_gold.py
    ├── test_models.py
    ├── test_setup.py
    └── __init__.py
```

## Ringkasan Struktur

| Folder | Deskripsi |
|---|---|
| `app/api/` | Endpoint REST (return JSON) — 12 blueprint |
| `app/models/` | Definisi tabel SQLAlchemy — 8 model |
| `app/services/` | Logika bisnis (budget, erosi, ETL, market, laporan) |
| `app/static/` | Aset statis: CSS (Tailwind + custom), JS (Chart.js), gambar |
| `app/templates/` | Template Jinja2 — 1 base + 12 halaman + partials |
| `app/views/` | Blueprint render HTML — 12 view |
| `docs/` | Spesifikasi, desain Stitch, prompt pengembangan |
| `dwh/` | Materi & artefak Data Warehouse (tugas akademik) |
| `migrations/` | Riwayat migrasi Flask-Migrate (Alembic) |
| `scripts/` | Skrip utilitas (import CSV) |
| `tests/` | Suite pytest — 11 file test |
