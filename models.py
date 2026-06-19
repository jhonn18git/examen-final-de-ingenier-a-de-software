from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Empresa(db.Model):
    __tablename__ = "empresa"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, default="JWLR Petrol")
    nit = db.Column(db.String(30), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=False)
    # Litros de cupo base para clientes nuevos sin historial
    cupo_base_inicial = db.Column(db.Float, nullable=False, default=20.0)
    # Factor de holgura decimal (ej. 0.10 = 10% sobre el promedio)
    factor_holgura = db.Column(db.Float, nullable=False, default=0.10)

    tanques = db.relationship("Tanque", backref="empresa", lazy=True)

    def __repr__(self):
        return f"<Empresa {self.nombre}>"


class Operador(db.Model):
    __tablename__ = "operador"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    # Roles posibles: 'admin', 'operador'
    rol = db.Column(db.String(20), nullable=False, default="operador")

    ventas = db.relationship("Venta", backref="operador", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Operador {self.usuario}>"


class Tanque(db.Model):
    __tablename__ = "tanque"

    id = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey("empresa.id"), nullable=False)
    identificador = db.Column(db.String(20), nullable=False)
    # 'Gasolina' o 'Diesel'
    tipo_carburante = db.Column(db.String(20), nullable=False)
    capacidad_maxima = db.Column(db.Float, nullable=False)
    stock_minimo = db.Column(db.Float, nullable=False)
    # Stock inicial cargado en seed; en runtime se calcula desde ingresos - ventas
    stock_actual = db.Column(db.Float, nullable=False, default=0.0)

    ingresos = db.relationship("Ingreso", backref="tanque", lazy=True)
    ventas = db.relationship("Venta", backref="tanque", lazy=True)

    def calcular_stock(self):
        total_ingresado = sum(i.litros for i in self.ingresos)
        total_vendido = sum(v.litros for v in self.ventas)
        return total_ingresado - total_vendido

    def __repr__(self):
        return f"<Tanque {self.identificador} ({self.tipo_carburante})>"


class Cliente(db.Model):
    __tablename__ = "cliente"

    id = db.Column(db.Integer, primary_key=True)
    cedula_nit = db.Column(db.String(20), nullable=False, unique=True)
    nombre_razon_social = db.Column(db.String(150), nullable=False)
    placa = db.Column(db.String(15), nullable=False)
    # 'Particular', 'Transporte Publico', 'Empresa'
    tipo_cliente = db.Column(db.String(30), nullable=False, default="Particular")
    # 'Activo', 'Suspendido'
    estado = db.Column(db.String(15), nullable=False, default="Activo")

    ventas = db.relationship("Venta", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nombre_razon_social} | {self.placa}>"


class Ingreso(db.Model):
    __tablename__ = "ingreso"

    id = db.Column(db.Integer, primary_key=True)
    id_tanque = db.Column(db.Integer, db.ForeignKey("tanque.id"), nullable=False)
    litros = db.Column(db.Float, nullable=False)
    nro_factura_remision = db.Column(db.String(50), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Ingreso {self.litros}L — Factura {self.nro_factura_remision}>"


class Venta(db.Model):
    __tablename__ = "venta"

    id = db.Column(db.Integer, primary_key=True)
    id_tanque = db.Column(db.Integer, db.ForeignKey("tanque.id"), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    id_operador = db.Column(db.Integer, db.ForeignKey("operador.id"), nullable=False)
    litros = db.Column(db.Float, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # Número de comprobante generado al confirmar la venta
    comprobante = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<Venta {self.comprobante} — {self.litros}L>"
