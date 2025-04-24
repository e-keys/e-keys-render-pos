from app import create_app, db
from app.models import Venta, Cliente, Producto, CredencialProducto
import json
from datetime import datetime

def restore_data():
    app = create_app()
    with app.app_context():
        try:
            # Leer datos del archivo
            with open('backup_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restaurar clientes
            for c_data in data['clientes']:
                cliente = Cliente(
                    id=c_data['id'],
                    nombre=c_data['nombre'],
                    telefono=c_data['telefono'],
                    email=c_data['email'],
                    direccion=c_data['direccion'],
                    notas=c_data['notas'],
                    created_at=datetime.fromisoformat(c_data['created_at']) if c_data['created_at'] else None
                )
                db.session.add(cliente)
            
            # Restaurar productos
            for p_data in data['productos']:
                producto = Producto(
                    id=p_data['id'],
                    codigo=p_data['codigo'],
                    nombre=p_data['nombre'],
                    descripcion=p_data['descripcion'],
                    tipo_id=p_data['tipo_id'],
                    precio_costo=p_data['precio_costo'],
                    precio_venta=p_data['precio_venta'],
                    stock=p_data['stock'],
                    stock_minimo=p_data['stock_minimo'],
                    duracion=p_data['duracion'],
                    proveedor_id=p_data['proveedor_id'],
                    created_at=datetime.fromisoformat(p_data['created_at']) if p_data['created_at'] else None,
                    updated_at=datetime.fromisoformat(p_data['updated_at']) if p_data['updated_at'] else None
                )
                db.session.add(producto)
            
            # Restaurar credenciales
            for c_data in data['credenciales']:
                credencial = CredencialProducto(
                    id=c_data['id'],
                    producto_id=c_data['producto_id'],
                    usuario=c_data['usuario'],
                    contrasena=c_data['contrasena'],
                    estado=c_data['estado'],
                    fecha_creacion=datetime.fromisoformat(c_data['fecha_creacion']) if c_data['fecha_creacion'] else None,
                    fecha_expiracion=datetime.fromisoformat(c_data['fecha_expiracion']) if c_data['fecha_expiracion'] else None
                )
                db.session.add(credencial)
            
            # Restaurar ventas
            for v_data in data['ventas']:
                venta = Venta(
                    id=v_data['id'],
                    cliente_id=v_data['cliente_id'],
                    producto_id=v_data['producto_id'],
                    credencial_id=v_data['credencial_id'],
                    cantidad=v_data['cantidad'],
                    precio_unitario=v_data['precio_unitario'],
                    total=v_data['total'],
                    canal_venta=v_data['canal_venta'],
                    estado=v_data['estado'],
                    notas=v_data['notas'],
                    fecha_venta=datetime.fromisoformat(v_data['fecha_venta']) if v_data['fecha_venta'] else None,
                    fecha_expiracion=datetime.fromisoformat(v_data['fecha_expiracion']) if v_data['fecha_expiracion'] else None,
                    created_at=datetime.fromisoformat(v_data['created_at']) if v_data['created_at'] else None,
                    descuento=0  # Valor por defecto para el nuevo campo
                )
                db.session.add(venta)
            
            db.session.commit()
            print("Datos restaurados exitosamente")
            
        except Exception as e:
            print(f"Error al restaurar datos: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    restore_data() 