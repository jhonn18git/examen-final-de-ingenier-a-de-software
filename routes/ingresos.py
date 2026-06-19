from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Ingreso, Tanque
from routes.utils import login_required

ingresos_bp = Blueprint("ingresos", __name__, url_prefix="/ingresos")


@ingresos_bp.route("/")
@login_required
def lista():
    todos = Ingreso.query.order_by(Ingreso.fecha_hora.desc()).all()
    return render_template("ingresos/lista.html", ingresos=todos)


@ingresos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    tanques = Tanque.query.all()

    if request.method == "POST":
        id_tanque = request.form.get("id_tanque", type=int)
        litros = request.form.get("litros", type=float)
        nro_factura = request.form.get("nro_factura_remision", "").strip()
        fecha_hora_str = request.form.get("fecha_hora", "").strip()

        errores = []
        if not id_tanque:
            errores.append("Seleccione un tanque.")
        if not litros or litros <= 0:
            errores.append("Ingrese una cantidad de litros válida.")
        if not nro_factura:
            errores.append("Ingrese el número de factura/remisión.")
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template("ingresos/nuevo.html", tanques=tanques,
                                   ahora=_ahora_str())

        tanque = db.session.get(Tanque, id_tanque)
        if tanque is None:
            flash("Tanque no encontrado.", "danger")
            return render_template("ingresos/nuevo.html", tanques=tanques,
                                   ahora=_ahora_str())

        disponible = tanque.capacidad_maxima - tanque.stock_actual
        if litros > disponible:
            flash(
                f"Cantidad supera la capacidad del tanque. "
                f"Espacio disponible: {disponible:.1f} L.",
                "danger",
            )
            return render_template("ingresos/nuevo.html", tanques=tanques,
                                   ahora=_ahora_str())

        fecha_hora = datetime.now()
        if fecha_hora_str:
            try:
                fecha_hora = datetime.fromisoformat(fecha_hora_str)
            except ValueError:
                pass

        ingreso = Ingreso(
            id_tanque=id_tanque,
            litros=litros,
            nro_factura_remision=nro_factura,
            fecha_hora=fecha_hora,
        )
        tanque.stock_actual += litros
        db.session.add(ingreso)
        db.session.commit()

        flash(
            f"Ingreso registrado. Stock de {tanque.identificador} "
            f"actualizado a {tanque.stock_actual:.1f} L.",
            "success",
        )
        return redirect(url_for("ingresos.lista"))

    return render_template("ingresos/nuevo.html", tanques=tanques, ahora=_ahora_str())


def _ahora_str():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")
