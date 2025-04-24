import os
from app import create_app, db
from app.models import User, Cliente, Producto, Proveedor, Venta

# Eliminar la base de datos si existe
if os.path.exists('app.db'):
    os.remove('app.db')
    print("Base de datos anterior eliminada.")

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    print("Base de datos creada correctamente.") 