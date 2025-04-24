from app import create_app, db
from app.models import Venta, Cliente, Producto, CredencialProducto
import json
from datetime import datetime

def backup_data():
    app = create_app()
    with app.app_context():
        try:
            # Obtener todos los datos
            ventas = Venta.query.all()
            clientes = Cliente.query.all()
            productos = Producto.query.all()
            credenciales = CredencialProducto.query.all()
            
            # Convertir a diccionarios
            data = {
                'ventas': [{
                    'id': v.id,
                    'cliente_id': v.cliente_id,
                    'producto_id': v.producto_id,
                    'credencial_id': v.credencial_id,
                    'cantidad': v.cantidad,
                    'precio_unitario': v.precio_unitario,
                    'total': v.total,
                    'canal_venta': v.canal_venta,
                    'estado': v.estado,
                    'notas': v.notas,
                    'fecha_venta': v.fecha_venta.isoformat() if v.fecha_venta else None,
                    'fecha_expiracion': v.fecha_expiracion.isoformat() if v.fecha_expiracion else None,
                    'created_at': v.created_at.isoformat() if v.created_at else None
                } for v in ventas],
                'clientes': [{
                    'id': c.id,
                    'nombre': c.nombre,
                    'telefono': c.telefono,
                    'email': c.email,
                    'direccion': c.direccion,
                    'notas': c.notas,
                    'created_at': c.created_at.isoformat() if c.created_at else None
                } for c in clientes],
                'productos': [{
                    'id': p.id,
                    'codigo': p.codigo,
                    'nombre': p.nombre,
                    'descripcion': p.descripcion,
                    'tipo_id': p.tipo_id,
                    'precio_costo': p.precio_costo,
                    'precio_venta': p.precio_venta,
                    'stock': p.stock,
                    'stock_minimo': p.stock_minimo,
                    'duracion': p.duracion,
                    'proveedor_id': p.proveedor_id,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'updated_at': p.updated_at.isoformat() if p.updated_at else None
                } for p in productos],
                'credenciales': [{
                    'id': c.id,
                    'producto_id': c.producto_id,
                    'usuario': c.usuario,
                    'contrasena': c.contrasena,
                    'estado': c.estado,
                    'fecha_creacion': c.fecha_creacion.isoformat() if c.fecha_creacion else None,
                    'fecha_expiracion': c.fecha_expiracion.isoformat() if c.fecha_expiracion else None
                } for c in credenciales]
            }
            
            # Guardar en archivo
            with open('backup_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print("Backup completado exitosamente")
            
        except Exception as e:
            print(f"Error al hacer backup: {str(e)}")

if __name__ == '__main__':
    backup_data() 