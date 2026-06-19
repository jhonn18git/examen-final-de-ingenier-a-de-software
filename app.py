import os
from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.ingresos import ingresos_bp
    from routes.ventas import ventas_bp
    from routes.clientes import clientes_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ingresos_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(clientes_bp)

    with app.app_context():
        db.create_all()
        _auto_seed_if_empty()

    return app


def _auto_seed_if_empty():
    from models import Empresa
    if Empresa.query.count() == 0:
        from seed import auto_seed
        auto_seed()


# Instancia a nivel de módulo para gunicorn (app:app)
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
