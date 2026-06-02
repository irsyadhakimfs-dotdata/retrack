# Blueprint dashboard_views — halaman dashboard utama

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Buat blueprint dengan nama 'dashboard_views'
bp = Blueprint('dashboard_views', __name__)


@bp.route('/dashboard')
@login_required
def dashboard():
    """Render halaman dashboard — hanya untuk pengguna yang sudah login."""
    return render_template('dashboard.html')
