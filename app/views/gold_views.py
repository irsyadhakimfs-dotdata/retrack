# Blueprint gold_views — halaman investasi emas (catatan kepemilikan + grafik)

from flask import Blueprint, render_template, current_app
from flask_login import login_required

# Buat blueprint dengan nama 'gold_views'
bp = Blueprint('gold_views', __name__)


@bp.route('/gold')
@login_required
def gold():
    """Render halaman investasi emas — kirim interval refresh dari config."""
    refresh_hours = current_app.config.get("MARKET_REFRESH_HOURS", 6)
    return render_template('gold/index.html', refresh_hours=refresh_hours)
