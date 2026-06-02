# Blueprint wallet_views — halaman manajemen dompet

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'wallet_views'
bp = Blueprint('wallet_views', __name__)


@bp.route('/wallets')
@login_required
def wallets():
    """Render halaman daftar dompet — hanya untuk pengguna yang sudah login."""
    return render_template('wallets/index.html')
