# Blueprint auth_views — halaman login, register, dan logout (HTML)

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, logout_user

# Buat blueprint dengan nama 'auth_views'
bp = Blueprint('auth_views', __name__)


@bp.route('/')
def index():
    """Root URL — arahkan ke dashboard jika sudah login, atau ke login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_views.dashboard'))
    return redirect(url_for('auth_views.login'))


@bp.route('/login')
def login():
    """Halaman login — redirect ke dashboard jika sudah login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_views.dashboard'))
    return render_template('auth/login.html')


@bp.route('/register')
def register():
    """Halaman register — redirect ke dashboard jika sudah login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_views.dashboard'))
    return render_template('auth/register.html')


@bp.route('/logout')
def logout():
    """Logout dan redirect ke halaman login."""
    logout_user()
    return redirect(url_for('auth_views.login'))
