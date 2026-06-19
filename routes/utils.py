from functools import wraps
from datetime import datetime, timedelta
from flask import session, redirect, url_for
from models import Venta, Empresa


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "operador_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def calcular_cupo(cliente_id):
    """
    Ps = total litros últimos 28 días / 4 semanas
    Si el cliente no tiene historial, usa cupo_base_inicial de Empresa.
    Retorna (ps, limite, es_nuevo).
    """
    empresa = Empresa.query.first()
    hace_28_dias = datetime.now() - timedelta(days=28)

    ventas_recientes = Venta.query.filter(
        Venta.id_cliente == cliente_id,
        Venta.fecha_hora >= hace_28_dias,
    ).all()

    total_litros = sum(v.litros for v in ventas_recientes)

    if total_litros == 0:
        ps = empresa.cupo_base_inicial
        es_nuevo = True
    else:
        ps = total_litros / 4
        es_nuevo = False

    limite = round(ps * (1 + empresa.factor_holgura), 2)
    ps = round(ps, 2)
    return ps, limite, es_nuevo
