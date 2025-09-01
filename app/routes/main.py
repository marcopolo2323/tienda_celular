from flask import Blueprint, render_template
from flask_login import login_required
from app.models import db, Celular, Accesorio, Venta, Servicio
from datetime import datetime
from app.utils.dashboard import get_dashboard_stats

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    stats = get_dashboard_stats()
    return render_template('index.html', **stats)