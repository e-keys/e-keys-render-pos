from app import create_app, db
from app.models import Venta
from datetime import datetime
from sqlalchemy import text

def check_database():
    app = create_app()
    with app.app_context():
        try:
            # Verificar si la tabla venta tiene la columna fecha_expiracion
            result = db.session.execute(text("PRAGMA table_info(venta)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'fecha_expiracion' not in columns:
                print("La columna fecha_expiracion no existe en la tabla venta")
                # Agregar la columna si no existe
                db.session.execute(text("ALTER TABLE venta ADD COLUMN fecha_expiracion DATETIME"))
                db.session.commit()
                print("Columna fecha_expiracion agregada a la tabla venta")
            
            # Verificar si hay ventas con fecha_expiracion nula
            ventas_sin_fecha = Venta.query.filter(Venta.fecha_expiracion.is_(None)).all()
            if ventas_sin_fecha:
                print(f"Se encontraron {len(ventas_sin_fecha)} ventas sin fecha de expiración")
                for venta in ventas_sin_fecha:
                    if venta.producto:
                        venta.fecha_expiracion = venta.fecha_venta + venta.producto.duracion
                        print(f"Fecha de expiración actualizada para la venta {venta.id}")
                db.session.commit()
                print("Fechas de expiración actualizadas")
            
            print("Verificación de base de datos completada")
            
        except Exception as e:
            print(f"Error al verificar la base de datos: {str(e)}")

if __name__ == "__main__":
    check_database() 