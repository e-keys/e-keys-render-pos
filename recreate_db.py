import os
import sys
import time
from app import create_app, db
from app.models import User, Cliente, Producto, Proveedor, Venta, CredencialProducto, TipoProducto
from sqlalchemy import inspect
from datetime import datetime, timedelta
from config import Config

def wait_for_file_unlock(file_path, max_attempts=5, delay=1):
    """Espera hasta que el archivo esté disponible para ser eliminado"""
    for _ in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except PermissionError:
            print(f"Archivo {file_path} bloqueado. Reintentando en {delay} segundos...")
            time.sleep(delay)
    return False

def recreate_database():
    app = create_app()
    
    with app.app_context():
        # Asegurarse de que el directorio instance exista
        if not os.path.exists(Config.INSTANCE_DIR):
            os.makedirs(Config.INSTANCE_DIR)
            print(f"Directorio {Config.INSTANCE_DIR} creado.")
        
        # Ruta absoluta de la base de datos
        db_path = os.path.join(Config.INSTANCE_DIR, 'app.db')
        
        # Intentar eliminar la base de datos existente
        if not wait_for_file_unlock(db_path):
            print("No se pudo eliminar la base de datos. Asegúrese de que no esté en uso.")
            sys.exit(1)
        
        print("Base de datos anterior eliminada.")
        
        # Eliminar todas las tablas
        db.drop_all()
        print("Tablas eliminadas correctamente.")
        
        # Crear todas las tablas
        db.create_all()
        print("Base de datos creada correctamente.")
        
        # Mostrar las tablas creadas
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("\nTablas en la base de datos:")
        for table in tables:
            print(f"- {table}")
            columns = inspector.get_columns(table)
            for column in columns:
                print(f"  * {column['name']}: {column['type']}")
        
        # Crear tipos de producto por defecto
        tipos_producto = [
            TipoProducto(nombre='Streaming', descripcion='Servicios de streaming (Netflix, Disney+, etc.)'),
            TipoProducto(nombre='Música', descripcion='Servicios de música (Spotify, Apple Music, etc.)'),
            TipoProducto(nombre='Juegos', descripcion='Servicios de juegos (Xbox Game Pass, PlayStation Plus, etc.)'),
            TipoProducto(nombre='Software', descripcion='Software y aplicaciones'),
            TipoProducto(nombre='Otros', descripcion='Otros tipos de productos')
        ]
        
        for tipo in tipos_producto:
            db.session.add(tipo)
        
        try:
            db.session.commit()
            print("Tipos de producto creados correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear tipos de producto: {str(e)}")
            raise
        
        # Crear usuario administrador
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            nombre='Administrador'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        try:
            db.session.commit()
            print("Usuario administrador creado: admin / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear usuario administrador: {str(e)}")
            raise
        
        # Crear algunos productos de ejemplo
        productos = [
            {
                'codigo': 'NETFLIX-1',
                'nombre': 'Netflix Premium',
                'descripcion': 'Cuenta Netflix Premium 4K',
                'tipo_id': 1,  # Streaming
                'precio_costo': 100,
                'precio_venta': 150,
                'stock': 0,
                'stock_minimo': 5,
                'duracion': 30
            },
            {
                'codigo': 'SPOTIFY-1',
                'nombre': 'Spotify Premium',
                'descripcion': 'Cuenta Spotify Premium',
                'tipo_id': 2,  # Música
                'precio_costo': 50,
                'precio_venta': 75,
                'stock': 0,
                'stock_minimo': 5,
                'duracion': 30
            }
        ]
        
        for producto_data in productos:
            producto = Producto(**producto_data)
            db.session.add(producto)
        
        try:
            db.session.commit()
            print("Productos de ejemplo creados correctamente.")
            print("\nBase de datos recreada exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear productos: {str(e)}")
            raise

if __name__ == '__main__':
    try:
        recreate_database()
    except Exception as e:
        print(f"\nError al recrear la base de datos: {str(e)}")
        sys.exit(1) 