from flask import request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Objek ekstensi dibuat di sini, diinisialisasi di create_app()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Tentukan halaman login untuk Flask-Login
login_manager.login_view = "auth_views.login"


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect ke halaman login untuk request HTML; kembalikan JSON 401 untuk API."""
    # Jika request ke endpoint API, kembalikan JSON
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Login diperlukan"}), 401
    # Untuk halaman HTML, redirect ke halaman login
    return redirect(url_for("auth_views.login"))
