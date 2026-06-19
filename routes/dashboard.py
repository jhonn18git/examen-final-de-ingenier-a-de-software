from flask import Blueprint, render_template
from models import Empresa, Tanque, Venta
from routes.utils import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    empresa = Empresa.query.first()
    tanques = Tanque.query.all()
    ultimas_ventas = Venta.query.order_by(Venta.fecha_hora.desc()).limit(5).all()
    tanques_alerta = [t for t in tanques if t.stock_actual <= t.stock_minimo]

    return render_template(
        "dashboard/index.html",
        empresa=empresa,
        tanques=tanques,
        ultimas_ventas=ultimas_ventas,
        tanques_alerta=tanques_alerta,
    )
