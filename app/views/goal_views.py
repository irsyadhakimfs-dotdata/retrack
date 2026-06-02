# Blueprint goal_views — halaman manajemen tabungan & goal

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'goal_views'
bp = Blueprint('goal_views', __name__)


@bp.route('/goals')
@login_required
def goals():
    """Render halaman daftar goal tabungan — hanya untuk pengguna yang sudah login."""
    return render_template('goals/index.html')
