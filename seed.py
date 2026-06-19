"""
seed.py — Datos de prueba para JWLR Petrol.
  python seed.py          → reset completo (drop + create + insert)
  auto_seed()             → solo inserta datos en BD vacía (llamado desde app.py)
"""
from datetime import datetime, timedelta


def auto_seed():
    """
    Inserta datos iniciales dentro del app context ya activo.
    No hace drop/create — las tablas deben existir.
    """
    from models import db, Empresa, Operador, Tanque, Cliente, Ingreso, Venta

    ahora = datetime.now()

    empresa = Empresa(
        nombre="JWLR Petrol",
        nit="1234567890",
        direccion="Av. Petrolera Km 3, Zona Norte",
        ciudad="Sucre",
        contacto="Tel: 591-4-6451234 | jwlr@petrol.bo",
        cupo_base_inicial=20.0,
        factor_holgura=0.10,
    )
    db.session.add(empresa)
    db.session.flush()

    tg = Tanque(id_empresa=empresa.id, identificador="T-01",
                tipo_carburante="Gasolina", capacidad_maxima=10000.0,
                stock_minimo=500.0, stock_actual=0.0)
    td = Tanque(id_empresa=empresa.id, identificador="T-02",
                tipo_carburante="Diesel", capacidad_maxima=15000.0,
                stock_minimo=800.0, stock_actual=0.0)
    db.session.add_all([tg, td])
    db.session.flush()

    admin = Operador(nombre="Administrador JWLR", usuario="admin", rol="admin")
    admin.set_password("admin123")
    playero = Operador(nombre="Carlos Mamani", usuario="playero1", rol="operador")
    playero.set_password("playero123")
    db.session.add_all([admin, playero])
    db.session.flush()

    c1 = Cliente(cedula_nit="7654321", nombre_razon_social="Juan Perez Flores",
                 placa="1234-ABC", tipo_cliente="Particular", estado="Activo")
    c2 = Cliente(cedula_nit="9876543", nombre_razon_social="Transportes del Sur S.R.L.",
                 placa="9876-TRA", tipo_cliente="Transporte Publico", estado="Activo")
    c3 = Cliente(cedula_nit="1122334", nombre_razon_social="Empresa Constructora Andina",
                 placa="5678-EMP", tipo_cliente="Empresa", estado="Activo")
    db.session.add_all([c1, c2, c3])
    db.session.flush()

    db.session.add_all([
        Ingreso(id_tanque=tg.id, litros=7000.0,
                nro_factura_remision="FACT-2024-001",
                fecha_hora=ahora - timedelta(days=30)),
        Ingreso(id_tanque=td.id, litros=12000.0,
                nro_factura_remision="FACT-2024-002",
                fecha_hora=ahora - timedelta(days=30)),
        Ingreso(id_tanque=tg.id, litros=3000.0,
                nro_factura_remision="FACT-2024-015",
                fecha_hora=ahora - timedelta(days=10)),
    ])
    db.session.flush()

    ventas_data = [
        (tg.id, c1.id, playero.id,  8.0, 28, "V-0001"),
        (tg.id, c1.id, playero.id, 12.0, 21, "V-0002"),
        (tg.id, c1.id, playero.id, 10.0, 14, "V-0003"),
        (tg.id, c1.id, playero.id,  9.0,  7, "V-0004"),
        (td.id, c2.id, playero.id, 38.0, 27, "V-0005"),
        (td.id, c2.id, playero.id, 42.0, 20, "V-0006"),
        (td.id, c2.id, playero.id, 40.0, 13, "V-0007"),
        (td.id, c2.id, playero.id, 39.0,  6, "V-0008"),
        (td.id, c3.id, admin.id,   25.0, 26, "V-0009"),
        (td.id, c3.id, admin.id,   22.0, 19, "V-0010"),
        (td.id, c3.id, admin.id,   28.0, 12, "V-0011"),
        (td.id, c3.id, admin.id,   25.0,  5, "V-0012"),
    ]
    db.session.add_all([
        Venta(id_tanque=it, id_cliente=ic, id_operador=io,
              litros=l, fecha_hora=ahora - timedelta(days=d), comprobante=c)
        for it, ic, io, l, d, c in ventas_data
    ])
    db.session.commit()

    for tanque in [tg, td]:
        tanque.stock_actual = tanque.calcular_stock()
    db.session.commit()

    print("JWLR Petrol - Datos de prueba cargados.")


def seed():
    """Reset completo: drop + create + insert. Uso: python seed.py"""
    from app import create_app
    from models import db
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        auto_seed()
        print("Seed completado.")


if __name__ == "__main__":
    seed()
