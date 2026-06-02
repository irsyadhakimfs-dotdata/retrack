"""Test Fase 3a — Auth API (register, login, logout, akses terproteksi)."""
import pytest


def register(client, email="user@test.com", password="pass123", name="User Test"):
    return client.post("/api/auth/register",
                       json={"email": email, "password": password, "name": name})


def login(client, email="user@test.com", password="pass123"):
    return client.post("/api/auth/login", json={"email": email, "password": password})


class TestRegister:
    def test_register_berhasil(self, client):
        resp = register(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["data"]["email"] == "user@test.com"

    def test_register_email_duplikat(self, client):
        register(client, email="duplikat@test.com")
        resp = register(client, email="duplikat@test.com")
        assert resp.status_code == 409
        assert resp.get_json()["ok"] is False

    def test_register_field_kosong(self, client):
        resp = client.post("/api/auth/register", json={"email": "", "password": "x", "name": "A"})
        assert resp.status_code == 400
        assert resp.get_json()["ok"] is False

    def test_register_tanpa_password(self, client):
        resp = client.post("/api/auth/register", json={"email": "a@b.com", "name": "A"})
        assert resp.status_code == 400


class TestLogin:
    def test_login_berhasil(self, client):
        register(client, email="login@test.com")
        resp = login(client, email="login@test.com")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_login_password_salah(self, client):
        register(client, email="salah@test.com")
        resp = login(client, email="salah@test.com", password="SALAH")
        assert resp.status_code == 401
        assert resp.get_json()["ok"] is False

    def test_login_email_tidak_ada(self, client):
        resp = login(client, email="tidakada@test.com")
        assert resp.status_code == 401


class TestLogout:
    def test_logout_berhasil(self, client):
        register(client, email="logout@test.com")
        login(client, email="logout@test.com")
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_logout_tanpa_login_ditolak(self, client):
        # Klien baru tanpa sesi login
        resp = client.post("/api/auth/logout")
        # Flask-Login redirect ke login view; kita pastikan bukan 200
        assert resp.status_code != 200


class TestAksesProteksi:
    def test_endpoint_terproteksi_tanpa_login(self, client):
        """Akses endpoint @login_required tanpa login harus ditolak (bukan 200)."""
        resp = client.post("/api/auth/logout")
        assert resp.status_code != 200
