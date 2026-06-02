# Blueprint transaction_views — halaman daftar transaksi

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'transaction_views'
bp = Blueprint('transaction_views', __name__)


@bp.route('/transactions')
@login_required
def transactions():
    """Render halaman daftar transaksi — hanya untuk pengguna yang sudah login."""
    return render_template('transactions/index.html')
