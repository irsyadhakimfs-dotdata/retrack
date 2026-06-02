# 01 — Skema Database

SQLite via SQLAlchemy. Uang = **Integer rupiah** (hindari float). Tiap tabel
punya `id` PK autoincrement.

## Relasi
```
User 1───* Wallet | Category | Transaction | Budget | SavingsGoal
Wallet 1───* Transaction
Category 1───* Transaction | Budget
```

## User
id · email (String120, unique, not null) · password_hash (String255) ·
name (String80) · created_at (DateTime default now).
Method `set_password`/`check_password` (werkzeug). Pakai UserMixin Flask-Login.

## Wallet
id · user_id FK · name (String80) · type ("cash"/"bank"/"ewallet") ·
initial_balance (Integer default 0).
> Saldo berjalan = initial_balance + Σ(income) − Σ(expense). Hitung di service,
> jangan simpan kolom saldo statis (hindari data basi).

## Category
id · user_id FK · name (String60) · kind ("income"/"expense") · icon (nullable).

## Transaction
id · user_id FK · wallet_id FK · category_id FK · amount (Integer, positif) ·
kind ("income"/"expense") · date (Date) · note (nullable) · created_at ·
**`usd_rate_at_date` (Float)** — WAJIB terisi untuk transaksi income (dasar
fitur erosi yang masuk MVP); diisi otomatis dari market_service saat transaksi
dibuat. Boleh null untuk expense.

## Budget
id · user_id FK · category_id FK · month (1-12) · year · limit_amount (Integer).
Unik per (user, category, month, year).

## SavingsGoal
id · user_id FK · name (String80) · target_amount (Integer) ·
saved_amount (Integer default 0) · deadline (Date nullable).
> Progress % = saved/target × 100. Estimasi/bulan = sisa target / sisa bulan.
