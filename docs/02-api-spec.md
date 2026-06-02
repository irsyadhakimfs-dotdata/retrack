# 02 — Spesifikasi API

Prefix `/api`. SELALU JSON. `@login_required`. Hanya akses data milik user login.
Format sukses: `{"ok": true, "data": {...}}` — error: `{"ok": false, "error": "..."}`.

## auth — app/api/auth.py
POST `/api/auth/register` (email, password, name) · POST `/api/auth/login` ·
POST `/api/auth/logout`.

## wallets — app/api/wallets.py
GET `/api/wallets` (+ saldo terhitung) · POST · PUT `/<id>` ·
DELETE `/<id>` (tolak jika masih ada transaksi).

## categories — app/api/categories.py
GET `/api/categories?kind=expense` · POST · PUT `/<id>` · DELETE `/<id>`.

## transactions — app/api/transactions.py
GET `/api/transactions?month=&year=&category_id=&q=` · POST · PUT `/<id>` ·
DELETE `/<id>`.
> Setelah create/update/delete, saldo wallet otomatis benar (dihitung ulang).
> Saat POST income: simpan kurs USD/IDR tanggal transaksi ke `usd_rate_at_date`.
> Saat GET income (punya usd_rate_at_date): sertakan objek `erosi`
> `{nilai_usd_awal, nilai_usd_sekarang, erosi_persen}` memakai kurs sekarang.

## budgets — app/api/budgets.py (pakai budget_service)
GET `/api/budgets?month=&year=` (+ terpakai, sisa, status) · POST · PUT · DELETE.
> status: "aman" / "hampir" (>=80%) / "lewat" (>100%).

## goals — app/api/goals.py
GET `/api/goals` (+ progress %, estimasi/bulan) · POST · PUT (juga untuk setor) ·
DELETE.

## reports — app/api/reports.py (pakai report_service)
GET `/api/reports/summary?month=&year=` · `/by-category` · `/trend?months=6`.

## market — app/api/market.py (pakai market_service)
GET `/api/market/usd-idr` · `/api/market/gold`.
> Cache 1 jam + fallback ke cache terakhir bila API down (jangan crash).

## export
GET `/api/export/csv` — unduh seluruh transaksi.
