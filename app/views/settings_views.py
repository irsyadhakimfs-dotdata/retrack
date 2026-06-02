# Blueprint settings_views — halaman pengaturan akun

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'settings_views'
bp = Blueprint('settings_views', __name__)


@bp.route('/settings')
@login_required
def settings():
    """Render halaman pengaturan profil dan preferensi — hanya untuk pengguna yang sudah login."""
    return render_template('settings/index.html')
