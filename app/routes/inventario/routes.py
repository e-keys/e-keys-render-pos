from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from app.models import Producto, Proveedor, Venta, TipoProducto, CredencialProducto
from app import db
from sqlalchemy import func
from datetime import datetime
from app.routes.inventario import inventario_bp

@inventario_bp.route('/')
@login_required
def index():
    # Obtener parámetros de filtro
    buscar = request.args.get('buscar', '')
    proveedor_id = request.args.get('proveedor_id', type=int)
    stock = request.args.get('stock')  # 'sin_stock', 'bajo_stock', 'con_stock'
    
    # Construir query base
    query = Producto.query.join(Proveedor)
    
    # Aplicar filtros
    if buscar:
        query = query.filter(Producto.nombre.ilike(f'%{buscar}%'))
    
    if proveedor_id:
        query = query.filter(Producto.proveedor_id == proveedor_id)
    
    if stock == 'sin_stock':
        query = query.filter(Producto.stock == 0)
    elif stock == 'bajo_stock':
        # Obtener todos los productos y filtrar los que tienen stock bajo
        productos = Producto.query.all()
        productos_ids = [p.id for p in productos if p.stock <= p.stock_minimo and p.stock > 0]
        query = query.filter(Producto.id.in_(productos_ids))
    elif stock == 'con_stock':
        # Obtener todos los productos y filtrar los que tienen stock
        productos = Producto.query.all()
        productos_ids = [p.id for p in productos if p.stock > p.stock_minimo]
        query = query.filter(Producto.id.in_(productos_ids))
    
    # Obtener productos con estadísticas
    productos = query.order_by(Producto.nombre).all()
    
    # Obtener todos los proveedores para el filtro
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    
    # Para cada producto, obtener estadísticas de ventas
    for producto in productos:
        # Ventas totales
        ventas_stats = db.session.query(
            func.count(Venta.id).label('total_ventas'),
            func.sum(Venta.total).label('total_ingresos')
        ).filter(Venta.producto_id == producto.id).first()
        
        producto.total_ventas = ventas_stats.total_ventas or 0
        producto.total_ingresos = ventas_stats.total_ingresos or 0
    
    return render_template('inventario/index.html',
                         productos=productos,
                         proveedores=proveedores,
                         buscar=buscar,
                         proveedor_id=proveedor_id,
                         stock=stock)

@inventario_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            descripcion = request.form.get('descripcion')
            tipo_id = request.form.get('tipo_id')
            precio_costo = float(request.form.get('precio_costo', 0))
            precio_venta = float(request.form.get('precio_venta', 0))
            stock_minimo = int(request.form.get('stock_minimo', 5))
            proveedor_id = request.form.get('proveedor_id')
            
            # Obtener el tipo de producto para usar su nombre
            tipo = TipoProducto.query.get_or_404(tipo_id)
            
            # Crear nuevo producto
            producto = Producto(
                codigo=f"PROD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",  # Generar código automáticamente
                nombre=tipo.nombre,  # Usar el nombre del tipo como nombre del producto
                descripcion=descripcion,
                tipo_id=tipo_id,
                precio_costo=precio_costo,
                precio_venta=precio_venta,
                stock_minimo=stock_minimo,
                proveedor_id=proveedor_id if proveedor_id else None
            )
            
            db.session.add(producto)
            db.session.commit()
            
            flash('Producto registrado exitosamente', 'success')
            return redirect(url_for('inventario.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el producto: {str(e)}', 'error')
            return redirect(url_for('inventario.nuevo'))
    
    proveedores = Proveedor.query.all()
    tipos_producto = TipoProducto.query.all()
    return render_template('inventario/nuevo.html', proveedores=proveedores, tipos_producto=tipos_producto)

@inventario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    producto = Producto.query.get_or_404(id)
    
    # Obtener estadísticas de ventas
    ventas_stats = db.session.query(
        func.count(Venta.id).label('total_ventas'),
        func.sum(Venta.total).label('total_ingresos')
    ).filter(Venta.producto_id == id).first()
    
    producto.total_ventas = ventas_stats.total_ventas or 0
    producto.total_ingresos = ventas_stats.total_ingresos or 0
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            precio_costo = float(request.form.get('precio_costo', 0))
            precio_venta = float(request.form.get('precio_venta', 0))
            
            # Validar que el precio de venta sea mayor al costo
            if precio_venta <= precio_costo:
                flash('El precio de venta debe ser mayor al precio de costo', 'error')
                return redirect(url_for('inventario.editar', id=id))
            
            # Actualizar datos del producto
            producto.nombre = request.form.get('nombre')
            producto.descripcion = request.form.get('descripcion')
            producto.precio_costo = precio_costo
            producto.precio_venta = precio_venta
            producto.stock_minimo = int(request.form.get('stock_minimo', 5))
            producto.duracion = int(request.form.get('duracion', 30))
            
            db.session.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('inventario.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
    
    return render_template('inventario/editar.html', producto=producto)

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    
    # Verificar si el producto tiene ventas asociadas
    if producto.ventas:
        flash('No se puede eliminar el producto porque tiene ventas asociadas', 'error')
        return redirect(url_for('inventario.index'))
    
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/detalles/<int:id>')
@login_required
def detalles(id):
    producto = Producto.query.get_or_404(id)
    
    # Obtener estadísticas de ventas
    stats = db.session.query(
        func.count(Venta.id).label('total_ventas'),
        func.sum(Venta.total).label('total_ingresos'),
        func.avg(Venta.total).label('precio_promedio')
    ).filter(Venta.producto_id == id).first()
    
    # Obtener ventas activas (no expiradas)
    ventas_activas = Venta.query.filter(
        Venta.producto_id == id,
        Venta.fecha_expiracion > datetime.now()
    ).order_by(Venta.fecha_expiracion).all()
    
    # Obtener últimas ventas
    ultimas_ventas = Venta.query.filter_by(producto_id=id)\
        .order_by(Venta.fecha_venta.desc())\
        .limit(10).all()
    
    # Obtener credenciales del producto
    credenciales = CredencialProducto.query.filter_by(producto_id=id)\
        .order_by(CredencialProducto.fecha_creacion.desc()).all()
    
    now = datetime.utcnow()
    
    return render_template('inventario/detalles.html',
                         producto=producto,
                         stats=stats,
                         ventas_activas=ventas_activas,
                         ultimas_ventas=ultimas_ventas,
                         credenciales=credenciales,
                         now=now)

@inventario_bp.route('/ajustar-stock/<int:id>', methods=['POST'])
@login_required
def ajustar_stock(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        cantidad = int(request.form.get('cantidad', 0))
        tipo_ajuste = request.form.get('tipo_ajuste')  # 'incrementar' o 'decrementar'
        
        if tipo_ajuste == 'incrementar':
            producto.stock += cantidad
        else:
            if producto.stock < cantidad:
                flash('No hay suficiente stock para realizar el ajuste', 'error')
                return redirect(url_for('inventario.detalles', id=id))
            producto.stock -= cantidad
        
        db.session.commit()
        flash('Stock ajustado exitosamente', 'success')
        
    except ValueError:
        flash('La cantidad debe ser un número entero', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al ajustar el stock: {str(e)}', 'error')
    
    return redirect(url_for('inventario.detalles', id=id))

@inventario_bp.route('/agregar_credenciales/<int:id>', methods=['POST'])
@login_required
def agregar_credenciales(id):
    producto = Producto.query.get_or_404(id)
    credenciales_texto = request.form.get('credenciales', '').strip()
    
    if not credenciales_texto:
        flash('No se proporcionaron credenciales', 'error')
        return redirect(url_for('inventario.detalles', id=id))
    
    try:
        # Procesar cada línea de credenciales
        for linea in credenciales_texto.split('\n'):
            if not linea.strip():
                continue
                
            try:
                usuario, contrasena = linea.strip().split(',')
                credencial = CredencialProducto(
                    producto_id=id,
                    usuario=usuario.strip(),
                    contrasena=contrasena.strip(),
                    estado='disponible',
                    fecha_creacion=datetime.utcnow()
                )
                db.session.add(credencial)
            except ValueError:
                flash(f'Formato inválido en la línea: {linea}', 'error')
                continue
        
        db.session.commit()
        flash('Credenciales agregadas exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar las credenciales: {str(e)}', 'error')
    
    return redirect(url_for('inventario.detalles', id=id))

@inventario_bp.route('/credenciales/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_credencial(id):
    credencial = CredencialProducto.query.get_or_404(id)
    
    try:
        db.session.delete(credencial)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@inventario_bp.route('/credenciales/<int:id>/editar', methods=['POST'])
@login_required
def editar_credencial(id):
    credencial = CredencialProducto.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'usuario' in data:
            credencial.usuario = data['usuario']
        if 'contrasena' in data:
            credencial.contrasena = data['contrasena']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@inventario_bp.route('/producto/<int:id>/credenciales')
@login_required
def obtener_credenciales_producto(id):
    """Ruta principal para obtener credenciales de un producto"""
    print(f'[DEBUG] Llamada a obtener_credenciales_producto con id={id}')
    
    credenciales = CredencialProducto.query.filter_by(
        producto_id=id,
        estado='disponible'
    ).all()
    
    return jsonify([{
        'id': c.id,
        'usuario': c.usuario,
        'estado': c.estado
    } for c in credenciales])

@inventario_bp.route('/credenciales/producto/<int:id>')
@login_required
def obtener_credenciales_producto_alternativa(id):
    """DEPRECATED: Usar /producto/<id>/credenciales en su lugar"""
    print('[DEPRECATED] Esta ruta será removida en futuras versiones. Usar /producto/<id>/credenciales')
    return obtener_credenciales_producto(id)

@inventario_bp.route('/credenciales/producto/<int:id>/disponibles')
@login_required
def obtener_credenciales_disponibles(id):
    """DEPRECATED: Usar /producto/<id>/credenciales en su lugar"""
    print('[DEPRECATED] Esta ruta será removida en futuras versiones. Usar /producto/<id>/credenciales')
    return obtener_credenciales_producto(id)

@inventario_bp.route('/test-credenciales')
@login_required
def test_credenciales():
    """Endpoint de prueba para verificar si hay credenciales disponibles"""
    credenciales = CredencialProducto.query.filter_by(estado='disponible').all()
    return jsonify({
        'total_credenciales': len(credenciales),
        'credenciales': [{
            'id': c.id,
            'producto_id': c.producto_id,
            'usuario': c.usuario,
            'estado': c.estado
        } for c in credenciales]
    })

@inventario_bp.route('/crear-credencial-prueba/<int:producto_id>', methods=['POST'])
@login_required
def crear_credencial_prueba(producto_id):
    """Endpoint para crear una credencial de prueba para un producto"""
    try:
        # Verificar que el producto existe
        producto = Producto.query.get_or_404(producto_id)
        
        # Crear una credencial de prueba
        credencial = CredencialProducto(
            producto_id=producto_id,
            usuario=f"usuario_prueba_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            contrasena="password123",
            estado='disponible',
            fecha_creacion=datetime.now()
        )
        
        db.session.add(credencial)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Credencial de prueba creada exitosamente',
            'credencial': {
                'id': credencial.id,
                'usuario': credencial.usuario,
                'estado': credencial.estado
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear credencial de prueba: {str(e)}'
        }), 500

@inventario_bp.route('/credenciales/<int:id>')
@login_required
def obtener_credencial(id):
    """Obtener detalles de una credencial específica"""
    credencial = CredencialProducto.query.get_or_404(id)
    return jsonify({
        'id': credencial.id,
        'usuario': credencial.usuario,
        'contrasena': credencial.contrasena,
        'estado': credencial.estado,
        'fecha_creacion': credencial.fecha_creacion.isoformat(),
        'fecha_expiracion': credencial.fecha_expiracion.isoformat() if credencial.fecha_expiracion else None
    }) 