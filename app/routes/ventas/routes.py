from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import Venta, Cliente, Producto, CredencialProducto
from app import db
from datetime import datetime, timedelta
from app.routes.ventas import ventas_bp

@ventas_bp.route('/')
@login_required
def index():
    # Obtener parámetros de filtro
    cliente = request.args.get('cliente', '')
    producto = request.args.get('producto', '')
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    canal = request.args.get('canal', '')
    status = request.args.get('status', '')

    # Construir query base
    query = Venta.query.join(Cliente).join(Producto).join(CredencialProducto)

    # Aplicar filtros
    if cliente:
        query = query.filter(Cliente.nombre.ilike(f'%{cliente}%'))
    if producto:
        query = query.filter(Producto.nombre.ilike(f'%{producto}%'))
    if fecha_inicio:
        query = query.filter(Venta.fecha_venta >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    if fecha_fin:
        query = query.filter(Venta.fecha_venta <= datetime.strptime(fecha_fin, '%Y-%m-%d'))
    if canal:
        query = query.filter(Venta.canal_venta == canal)
    if status:
        query = query.filter(Venta.estado == status)

    # Ordenar por fecha de venta descendente
    ventas = query.order_by(Venta.fecha_venta.desc()).all()
    
    # Calcular días restantes y ganancia para cada venta
    for venta in ventas:
        venta.dias_restantes = venta.calcular_dias_restantes()
        venta.ganancia = venta.calcular_ganancia()
        venta.estado_actual = venta.obtener_estado()
    
    # Obtener listas para los filtros
    clientes = Cliente.query.all()
    # Obtener todos los productos y filtrar los que tienen stock disponible
    productos = Producto.query.all()
    productos = [p for p in productos if p.stock > 0]
    canales_venta = ['WhatsApp', 'Llamada', 'Presencial', 'Email']
    estados = ['activo', 'vencido', 'cancelado']

    return render_template('ventas/index.html',
                         ventas=ventas,
                         clientes=clientes,
                         productos=productos,
                         canales_venta=canales_venta,
                         estados=estados,
                         now=datetime.now())

@ventas_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            producto_id = request.form.get('producto_id')
            credencial_id = request.form.get('credencial_id')
            cliente_id = request.form.get('cliente_id')
            precio_unitario = float(request.form.get('precio_unitario', 0))
            descuento = float(request.form.get('descuento', 0))
            fecha_venta = datetime.strptime(request.form.get('fecha_venta'), '%Y-%m-%d')
            fecha_expiracion = datetime.strptime(request.form.get('fecha_expiracion'), '%Y-%m-%d')
            
            # Obtener el producto y la credencial
            producto = Producto.query.get_or_404(producto_id)
            credencial = CredencialProducto.query.get_or_404(credencial_id)
            
            # Verificar que la credencial pertenece al producto
            if credencial.producto_id != producto.id:
                flash('La credencial seleccionada no pertenece al producto', 'error')
                return redirect(url_for('ventas.nuevo'))
            
            # Verificar que la credencial está disponible
            if credencial.estado != 'disponible':
                flash('La credencial seleccionada no está disponible', 'error')
                return redirect(url_for('ventas.nuevo'))
            
            # Crear la venta
            venta = Venta(
                cliente_id=cliente_id,
                producto_id=producto_id,
                credencial_id=credencial_id,
                cantidad=1,
                precio_unitario=precio_unitario,
                descuento=descuento,
                total=precio_unitario * (1 - descuento/100),
                canal_venta=request.form.get('canal_venta', 'otro'),
                fecha_venta=fecha_venta,
                fecha_expiracion=fecha_expiracion
            )
            
            # Actualizar estado de la credencial
            credencial.estado = 'activa'
            credencial.fecha_expiracion = fecha_expiracion
            
            db.session.add(venta)
            db.session.commit()
            
            flash('Venta registrada exitosamente', 'success')
            return redirect(url_for('ventas.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la venta: {str(e)}', 'error')
            return redirect(url_for('ventas.nuevo'))
    
    # GET request
    productos = Producto.query.all()
    clientes = Cliente.query.all()
    canales_venta = ['whatsapp', 'telegram', 'email', 'otro']
    
    return render_template('ventas/nuevo.html',
                         productos=productos,
                         clientes=clientes,
                         canales_venta=canales_venta)

@ventas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    # Obtener la venta con todas sus relaciones
    venta = Venta.query.join(Cliente).join(Producto).filter(Venta.id == id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            venta.precio_unitario = float(request.form['precio_unitario'])
            venta.descuento = float(request.form.get('descuento', 0))
            venta.canal_venta = request.form['canal_venta']
            venta.estado = request.form['estado']
            venta.notas = request.form.get('notas', '')
            
            # Actualizar fecha de expiración si se proporciona
            fecha_expiracion = request.form.get('fecha_expiracion')
            if fecha_expiracion:
                try:
                    fecha_exp = datetime.strptime(fecha_expiracion, '%Y-%m-%d')
                    venta.fecha_expiracion = fecha_exp
                except ValueError:
                    flash('Formato de fecha inválido. Use YYYY-MM-DD', 'error')
                    return redirect(url_for('ventas.editar', id=id))
            
            # Recalcular total
            venta.total = venta.precio_unitario * venta.cantidad * (1 - venta.descuento/100)
            
            # Si se cancela la venta, liberar las credenciales
            if venta.estado == 'cancelado':
                credenciales = CredencialProducto.query.filter_by(venta_id=venta.id).all()
                for credencial in credenciales:
                    credencial.estado = 'disponible'
                    credencial.venta_id = None
                venta.cantidad = 0
            
            db.session.commit()
            flash('Venta actualizada exitosamente', 'success')
            return redirect(url_for('ventas.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la venta: {str(e)}', 'error')
            return redirect(url_for('ventas.editar', id=id))
    
    # Obtener listas para los selectores
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    canales_venta = ['WhatsApp', 'Telegram', 'Email', 'Presencial', 'Instagram', 'Facebook', 'Otro']
    estados = ['Completada', 'Pendiente', 'Cancelada']
    
    return render_template('ventas/editar.html',
                         venta=venta,
                         clientes=clientes,
                         productos=productos,
                         canales_venta=canales_venta,
                         estados=estados,
                         now=datetime.now())

@ventas_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    venta = Venta.query.get_or_404(id)
    try:
        # Liberar la credencial asociada a la venta
        if venta.credencial:
            venta.credencial.estado = 'disponible'
            venta.credencial.fecha_expiracion = None
        
        db.session.delete(venta)
        db.session.commit()
        flash('Venta eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas.index'))

@ventas_bp.route('/ventas/<int:id>')
@login_required
def detalles(id):
    venta = Venta.query.get_or_404(id)
    venta.dias_restantes = venta.calcular_dias_restantes()
    venta.ganancia = venta.calcular_ganancia()
    venta.estado_actual = venta.obtener_estado()
    now = datetime.utcnow()
    return render_template('ventas/detalles.html', venta=venta, now=now) 