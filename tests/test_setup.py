"""Test Fase 1 — verifikasi setup dasar dan route /ping."""
import pytest
from app import create_app


@pytest.fixture
def client():
    """Buat test client dengan konfigurasi testing."""
    app = create_app("testing")
    with app.test_client() as c:
        yield c


def test_ping(client):
    """Route /ping harus mengembalikan JSON {'ok': True, 'message': 'pong'}."""
    resp = client.get("/ping")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["message"] == "pong"
