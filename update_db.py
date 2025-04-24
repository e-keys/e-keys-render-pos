from app import create_app, db
from app.models import Producto, CredencialProducto, Venta

def update_database():
    app = create_app()
    with app.app_context():
        try:
            # Crear las nuevas tablas
            db.create_all()
            
            # Eliminar la columna stock de la tabla producto
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE producto DROP COLUMN IF EXISTS stock')
            
            # Migrar datos existentes
            ventas = Venta.query.all()
            for venta in ventas:
                # Crear una nueva credencial para cada venta existente
                credencial = CredencialProducto(
                    producto_id=venta.producto_id,
                    usuario=venta.usuario,
                    contrasena=venta.password,
                    estado='vendido',
                    fecha_creacion=venta.fecha_venta,
                    fecha_expiracion=venta.fecha_expiracion
                )
                db.session.add(credencial)
                db.session.flush()  # Para obtener el ID de la credencial
                
                # Actualizar la venta con la nueva credencial
                venta.credencial_id = credencial.id
            
            # Eliminar las columnas antiguas de usuario y password
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE venta DROP COLUMN usuario')
                conn.execute('ALTER TABLE venta DROP COLUMN password')
            
            # Agregar columna de descuento si no existe
            db.session.execute('ALTER TABLE venta ADD COLUMN IF NOT EXISTS descuento FLOAT DEFAULT 0')
            
            db.session.commit()
            print("Base de datos actualizada exitosamente")
        except Exception as e:
            print(f"Error al actualizar la base de datos: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    update_database() 