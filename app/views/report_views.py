# Blueprint report_views — halaman laporan keuangan

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'report_views'
bp = Blueprint('report_views', __name__)


@bp.route('/reports')
@login_required
def reports():
    """Render halaman laporan dengan tiga grafik Chart.js — hanya untuk pengguna yang sudah login."""
    return render_template('reports/index.html')
