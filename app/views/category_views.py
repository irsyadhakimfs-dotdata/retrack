# Blueprint category_views — halaman manajemen kategori

from flask import Blueprint, render_template
from flask_login import login_required

# Buat blueprint dengan nama 'category_views'
bp = Blueprint('category_views', __name__)


@bp.route('/categories')
@login_required
def categories():
    """Render halaman daftar kategori — hanya untuk pengguna yang sudah login."""
    return render_template('categories/index.html')
