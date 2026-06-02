# Blueprint market_views — halaman kurs USD/IDR dan harga emas

from flask import Blueprint, render_template, current_app
from flask_login import login_required

# Buat blueprint dengan nama 'market_views'
bp = Blueprint('market_views', __name__)


@bp.route('/market')
@login_required
def market():
    """Render halaman market — kirim interval refresh dari config ke template."""
    refresh_hours = current_app.config.get("MARKET_REFRESH_HOURS", 6)
    return render_template('market/index.html', refresh_hours=refresh_hours)
