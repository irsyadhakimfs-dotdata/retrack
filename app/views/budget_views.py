# Blueprint budget_views — halaman manajemen anggaran

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'budget_views'
bp = Blueprint('budget_views', __name__)


@bp.route('/budgets')
@login_required
def budgets():
    """Render halaman daftar anggaran — hanya untuk pengguna yang sudah login."""
    return render_template('budgets/index.html')
