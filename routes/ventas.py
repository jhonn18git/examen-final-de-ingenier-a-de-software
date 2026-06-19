import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Venta, Cliente, Tanque, Empresa
from routes.utils import login_required, calcular_cupo

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")


@ventas_bp.route("/")
@login_required
def lista():
    todas = Venta.query.order_by(Venta.fecha_hora.desc()).all()
    return render_template("ventas/lista.html", ventas=todas)


# ── PASO 1: buscar cliente ────────────────────────────────────────────────────

@ventas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    if request.method == "POST":
        busqueda = request.form.get("busqueda", "").strip()
        tipo = request.form.get("tipo_carburante", "Gasolina")

        if not busqueda:
            flash("Ingrese una placa o cédula para buscar.", "warning")
            return render_template("ventas/buscar.html")

        cliente = Cliente.query.filter(
            (Cliente.placa == busqueda.upper()) |
            (Cliente.cedula_nit == busqueda)
        ).first()

        if cliente is None:
            return redirect(url_for(
                "ventas.nuevo_cliente",
                busqueda=busqueda,
                tipo=tipo,
            ))

        return redirect(url_for(
            "ventas.procesar",
            cliente_id=cliente.id,
            tipo=tipo,
        ))

    return render_template("ventas/buscar.html")


# ── PASO 1b: registro automático de cliente nuevo ─────────────────────────────

@ventas_bp.route("/nuevo-cliente", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    busqueda = request.args.get("busqueda", "")
    tipo = request.args.get("tipo", "Gasolina")

    if request.method == "POST":
        cedula_nit = request.form.get("cedula_nit", "").strip()
        nombre = request.form.get("nombre_razon_social", "").strip()
        placa = request.form.get("placa", "").strip().upper()
        tipo_cliente = request.form.get("tipo_cliente", "Particular")
        tipo = request.form.get("tipo_carburante", "Gasolina")

        errores = []
        if not cedula_nit:
            errores.append("Ingrese la cédula o NIT.")
        if not nombre:
            errores.append("Ingrese el nombre o razón social.")
        if not placa:
            errores.append("Ingrese la placa del vehículo.")
        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template("ventas/nuevo_cliente.html",
                                   busqueda=busqueda, tipo=tipo)

        existente = Cliente.query.filter_by(cedula_nit=cedula_nit).first()
        if existente:
            flash("Ya existe un cliente con esa cédula/NIT.", "warning")
            return redirect(url_for("ventas.procesar",
                                    cliente_id=existente.id, tipo=tipo))

        cliente = Cliente(
            cedula_nit=cedula_nit,
            nombre_razon_social=nombre,
            placa=placa,
            tipo_cliente=tipo_cliente,
            estado="Activo",
        )
        db.session.add(cliente)
        db.session.commit()

        flash(f"Cliente '{nombre}' registrado correctamente.", "success")
        return redirect(url_for("ventas.procesar",
                                cliente_id=cliente.id, tipo=tipo))

    return render_template("ventas/nuevo_cliente.html",
                           busqueda=busqueda, tipo=tipo)


# ── PASO 2: mostrar cupo y procesar venta ────────────────────────────────────

@ventas_bp.route("/procesar/<int:cliente_id>", methods=["GET", "POST"])
@login_required
def procesar(cliente_id):
    cliente = db.session.get(Cliente, cliente_id)
    if cliente is None:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("ventas.nueva"))

    tipo = request.args.get("tipo", request.form.get("tipo_carburante", "Gasolina"))
    empresa = Empresa.query.first()
    tanques = Tanque.query.filter_by(tipo_carburante=tipo).all()
    ps, limite, es_nuevo = calcular_cupo(cliente_id)

    if request.method == "POST":
        tipo = request.form.get("tipo_carburante", tipo)
        id_tanque = request.form.get("id_tanque", type=int)
        litros_form = request.form.get("litros", type=float)

        if not id_tanque or not litros_form or litros_form <= 0:
            flash("Seleccione tanque e ingrese una cantidad válida.", "danger")
            return render_template("ventas/procesar.html",
                                   cliente=cliente, tanques=tanques,
                                   ps=ps, limite=limite, es_nuevo=es_nuevo,
                                   tipo=tipo, empresa=empresa)

        if cliente.estado == "Suspendido":
            flash("El cliente está suspendido. No se puede procesar la venta.", "danger")
            return render_template("ventas/procesar.html",
                                   cliente=cliente, tanques=tanques,
                                   ps=ps, limite=limite, es_nuevo=es_nuevo,
                                   tipo=tipo, empresa=empresa)

        tanque = db.session.get(Tanque, id_tanque)
        if tanque is None:
            flash("Tanque no válido.", "danger")
            return render_template("ventas/procesar.html",
                                   cliente=cliente, tanques=tanques,
                                   ps=ps, limite=limite, es_nuevo=es_nuevo,
                                   tipo=tipo, empresa=empresa)

        # Aplicar límite de cupo (server-side siempre valida)
        litros_venta = litros_form
        ajustado = False
        if litros_form > limite:
            litros_venta = limite
            ajustado = True

        if tanque.stock_actual < litros_venta:
            flash(
                f"Stock insuficiente en {tanque.identificador}. "
                f"Disponible: {tanque.stock_actual:.1f} L.",
                "danger",
            )
            return render_template("ventas/procesar.html",
                                   cliente=cliente, tanques=tanques,
                                   ps=ps, limite=limite, es_nuevo=es_nuevo,
                                   tipo=tipo, empresa=empresa)

        comprobante = (
            f"VNT-{datetime.now().strftime('%Y%m%d')}"
            f"-{uuid.uuid4().hex[:6].upper()}"
        )
        venta = Venta(
            id_tanque=tanque.id,
            id_cliente=cliente.id,
            id_operador=session["operador_id"],
            litros=litros_venta,
            fecha_hora=datetime.now(),
            comprobante=comprobante,
        )
        tanque.stock_actual -= litros_venta
        db.session.add(venta)
        db.session.commit()

        if ajustado:
            flash(
                f"Cantidad ajustada al límite permitido ({limite:.1f} L). "
                f"Venta procesada correctamente.",
                "warning",
            )

        if tanque.stock_actual <= tanque.stock_minimo:
            flash(
                f"ALERTA DE STOCK: {tanque.identificador} tiene "
                f"{tanque.stock_actual:.1f} L, por debajo del mínimo "
                f"({tanque.stock_minimo:.1f} L).",
                "warning",
            )

        return redirect(url_for("ventas.comprobante", venta_id=venta.id))

    return render_template(
        "ventas/procesar.html",
        cliente=cliente,
        tanques=tanques,
        ps=ps,
        limite=limite,
        es_nuevo=es_nuevo,
        tipo=tipo,
        empresa=empresa,
    )


# ── Comprobante ───────────────────────────────────────────────────────────────

@ventas_bp.route("/comprobante/<int:venta_id>")
@login_required
def comprobante(venta_id):
    venta = db.session.get(Venta, venta_id)
    if venta is None:
        flash("Comprobante no encontrado.", "danger")
        return redirect(url_for("ventas.lista"))
    return render_template("ventas/comprobante.html", venta=venta)
