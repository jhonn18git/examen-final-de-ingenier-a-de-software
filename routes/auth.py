from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Operador

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "operador_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        if not usuario or not password:
            flash("Ingrese usuario y contraseña.", "warning")
            return render_template("auth/login.html")

        operador = Operador.query.filter_by(usuario=usuario).first()
        if operador and operador.check_password(password):
            session["operador_id"] = operador.id
            session["operador_nombre"] = operador.nombre
            session["operador_rol"] = operador.rol
            flash(f"Bienvenido, {operador.nombre}.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
