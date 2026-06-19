from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Cliente
from routes.utils import login_required

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes_bp.route("/")
@login_required
def lista():
    clientes = Cliente.query.order_by(Cliente.nombre_razon_social).all()
    return render_template("clientes/lista.html", clientes=clientes)


@clientes_bp.route("/<int:cliente_id>/toggle-estado", methods=["POST"])
@login_required
def toggle_estado(cliente_id):
    cliente = db.session.get(Cliente, cliente_id)
    if cliente is None:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes.lista"))

    cliente.estado = "Suspendido" if cliente.estado == "Activo" else "Activo"
    db.session.commit()
    flash(
        f"Cliente '{cliente.nombre_razon_social}' "
        f"{'suspendido' if cliente.estado == 'Suspendido' else 'reactivado'}.",
        "warning" if cliente.estado == "Suspendido" else "success",
    )
    return redirect(url_for("clientes.lista"))
