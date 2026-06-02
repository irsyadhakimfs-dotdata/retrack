from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, migrate, login_manager


def create_app(config_name="development"):
    """Application factory — buat dan konfigurasi Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inisialisasi ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import model di sini agar Alembic/Flask-Migrate bisa mendeteksi semua tabel
    with app.app_context():
        from app.models import (  # noqa: F401
            User, Wallet, Category, Transaction, Budget, SavingsGoal,
            GoldHolding,
            DimDate, DimUser, DimWallet, DimCategory, FactTransaction,
        )

        # Loader pengguna untuk Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    # Daftarkan blueprint API
    from app.api.auth import bp as auth_bp
    from app.api.wallets import bp as wallets_bp
    from app.api.categories import bp as categories_bp
    from app.api.transactions import bp as transactions_bp
    from app.api.budgets import bp as budgets_bp
    from app.api.goals import bp as goals_bp
    from app.api.reports import bp as reports_bp
    from app.api.market import bp as market_bp
    from app.api.export import bp as export_bp
    from app.api.user import bp as user_bp
    from app.api.dwh import bp as dwh_bp
    from app.api.gold import bp as gold_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(wallets_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(dwh_bp)
    app.register_blueprint(gold_bp)

    # Daftarkan blueprint Views (halaman HTML)
    from app.views.auth_views import bp as auth_views_bp
    from app.views.dashboard_views import bp as dashboard_views_bp
    from app.views.transaction_views import bp as transaction_views_bp
    from app.views.category_views import bp as category_views_bp
    from app.views.budget_views import bp as budget_views_bp
    from app.views.wallet_views import bp as wallet_views_bp
    from app.views.goal_views import bp as goal_views_bp
    from app.views.report_views import bp as report_views_bp
    from app.views.market_views import bp as market_views_bp
    from app.views.settings_views import bp as settings_views_bp
    from app.views.gold_views import bp as gold_views_bp
    app.register_blueprint(auth_views_bp)
    app.register_blueprint(dashboard_views_bp)
    app.register_blueprint(transaction_views_bp)
    app.register_blueprint(category_views_bp)
    app.register_blueprint(budget_views_bp)
    app.register_blueprint(wallet_views_bp)
    app.register_blueprint(goal_views_bp)
    app.register_blueprint(report_views_bp)
    app.register_blueprint(market_views_bp)
    app.register_blueprint(settings_views_bp)
    app.register_blueprint(gold_views_bp)

    # Versi aset untuk cache-busting CSS/JS.
    # Memakai timestamp saat server start → tiap restart memaksa browser
    # memuat ulang file statis (penting di dev agar perubahan langsung tampil).
    import time as _time
    asset_version = str(int(_time.time()))

    @app.context_processor
    def inject_asset_version():
        return {"asset_v": asset_version}

    # Route health-check sederhana
    @app.route("/ping")
    def ping():
        return jsonify({"ok": True, "message": "pong"})

    return app
