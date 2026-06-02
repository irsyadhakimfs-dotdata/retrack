# Paket views — mendaftarkan semua sub-blueprint halaman HTML

from flask import Blueprint

# Blueprint induk views (opsional, bisa dipakai sebagai namespace)
views_bp = Blueprint('views', __name__)

# Import semua sub-blueprint agar bisa didaftarkan di create_app()
from app.views import (  # noqa: F401, E402
    auth_views,
    dashboard_views,
    transaction_views,
    category_views,
    budget_views,
    wallet_views,
    goal_views,
    report_views,
    market_views,
    settings_views,
)
