# Blueprint dwh_views — halaman DWH Dashboard (Data Warehouse Mode)

from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("dwh_views", __name__)


@bp.route("/dwh-dashboard")
@login_required
def dwh_dashboard():
    """Render halaman Data Warehouse Dashboard."""
    tahun_sekarang = date.today().year
    return render_template("dwh/dashboard.html", tahun=tahun_sekarang)
