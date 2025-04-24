from app import create_app, db
from app.models import User, Cliente, Producto, Proveedor, Venta, CredencialProducto, TipoProducto

def init_database():
    app = create_app()
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            
            # Crear usuario administrador si no existe
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin')
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print('Usuario administrador creado: admin / admin123')
            
            print("Base de datos inicializada exitosamente")
            
        except Exception as e:
            print(f"Error al inicializar la base de datos: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    init_database() 