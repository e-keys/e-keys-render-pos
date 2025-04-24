from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from app.filters import format_currency

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'

    # Registrar filtros
    app.jinja_env.filters['format_currency'] = format_currency

    with app.app_context():
        # Importar rutas y modelos
        from app.models import User, Cliente, Producto, Proveedor, Venta, CredencialProducto, TipoProducto
        
        # Registrar blueprints
        from app.routes.auth import auth_bp
        from app.routes.main import main_bp
        from app.routes.ventas import ventas_bp
        from app.routes.clientes import clientes_bp
        from app.routes.proveedores import proveedores_bp
        from app.routes.inventario import inventario_bp
        from app.routes.inventario.credenciales import credenciales_bp
        from app.routes.tipos_producto import tipos_producto_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(ventas_bp)
        app.register_blueprint(clientes_bp)
        app.register_blueprint(proveedores_bp)
        app.register_blueprint(inventario_bp)
        app.register_blueprint(credenciales_bp)
        app.register_blueprint(tipos_producto_bp)

        # Crear tablas de la base de datos
        db.create_all()

        # Crear usuario administrador si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('Usuario administrador creado: admin / admin123')

        return app 