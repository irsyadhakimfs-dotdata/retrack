"""Verifikasi sementara fitur 'last N days' (summary, by-category, transactions, trend)."""
from datetime import date, timedelta


def _auth(client, email, password="pass", name="U"):
    client.post("/api/auth/register", json={"email": email, "password": password, "name": name})
    client.post("/api/auth/login", json={"email": email, "password": password})


def _wc(client):
    wid = client.post("/api/wallets", json={"name": "W", "type": "cash"}).get_json()["data"]["id"]
    cid = client.post("/api/categories", json={"name": "Gaji", "kind": "income"}).get_json()["data"]["id"]
    cid2 = client.post("/api/categories", json={"name": "Makan", "kind": "expense"}).get_json()["data"]["id"]
    return wid, cid, cid2


def test_days_mode_lintas_bulan(client):
    _auth(client, "days@test.com")
    wid, cid, cid2 = _wc(client)
    hari_ini = date.today()
    d5 = (hari_ini - timedelta(days=5)).isoformat()      # masuk 30 hari
    d40 = (hari_ini - timedelta(days=40)).isoformat()    # luar 30 hari, dalam 90
    d150 = (hari_ini - timedelta(days=150)).isoformat()  # dalam 180

    client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid, "amount": 1_000_000, "kind": "income", "date": d5})
    client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2, "amount": 200_000, "kind": "expense", "date": d5})
    client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2, "amount": 300_000, "kind": "expense", "date": d40})
    client.post("/api/transactions", json={"wallet_id": wid, "category_id": cid2, "amount": 500_000, "kind": "expense", "date": d150})

    # summary 30 hari → hanya transaksi d5
    s30 = client.get("/api/reports/summary?days=30").get_json()["data"]
    assert s30["income"] == 1_000_000 and s30["expense"] == 200_000

    # summary 90 hari → d5 + d40
    s90 = client.get("/api/reports/summary?days=90").get_json()["data"]
    assert s90["expense"] == 500_000  # 200k + 300k

    # summary 180 hari → semua expense
    s180 = client.get("/api/reports/summary?days=180").get_json()["data"]
    assert s180["expense"] == 1_000_000  # 200k+300k+500k

    # by-category 30 hari → hanya Makan 200k
    c30 = client.get("/api/reports/by-category?days=30").get_json()["data"]
    assert len(c30) == 1 and c30[0]["total"] == 200_000

    # transactions days=30 → 2 transaksi (income+expense d5)
    t30 = client.get("/api/transactions?days=30").get_json()["data"]
    assert len(t30) == 2

    # trend-daily days=90 → 90 titik
    tr = client.get("/api/reports/trend-daily?days=90").get_json()
    assert len(tr["data"]) == 90 and len(tr["chart"]["labels"]) == 90
