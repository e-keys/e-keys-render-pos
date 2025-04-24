from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models import Cliente, Venta
from app import db
from sqlalchemy import func
from datetime import datetime
from app.routes.clientes import clientes_bp

@clientes_bp.route('/')
@login_required
def index():
    # Obtener parámetros de búsqueda
    buscar = request.args.get('buscar', '')
    estado = request.args.get('estado')  # 'activo', 'inactivo'
    
    # Construir query base
    query = Cliente.query
    
    # Aplicar filtros
    if buscar:
        query = query.filter(
            Cliente.nombre.ilike(f'%{buscar}%') |
            Cliente.telefono.ilike(f'%{buscar}%') |
            Cliente.email.ilike(f'%{buscar}%')
        )
    
    if estado:
        if estado == 'activo':
            # Clientes con al menos una licencia activa
            query = query.filter(
                Cliente.ventas.any(Venta.fecha_expiracion > datetime.now())
            )
        elif estado == 'inactivo':
            # Clientes sin licencias activas
            query = query.filter(
                ~Cliente.ventas.any(Venta.fecha_expiracion > datetime.now())
            )
    
    # Obtener clientes con estadísticas
    clientes = query.order_by(Cliente.nombre).all()
    
    # Para cada cliente, obtener estadísticas
    for cliente in clientes:
        # Total de ventas y monto
        ventas_stats = db.session.query(
            func.count(Venta.id).label('total_ventas'),
            func.sum(Venta.total).label('total_gastado')
        ).filter(Venta.cliente_id == cliente.id).first()
        
        cliente.total_ventas = ventas_stats.total_ventas or 0
        cliente.total_gastado = ventas_stats.total_gastado or 0
        
        # Licencias activas
        cliente.licencias_activas = Venta.query.filter(
            Venta.cliente_id == cliente.id,
            Venta.fecha_expiracion > datetime.now()
        ).count()
    
    return render_template('clientes/index.html',
                         clientes=clientes,
                         buscar=buscar,
                         estado=estado)

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            direccion = request.form.get('direccion')
            notas = request.form.get('notas')
            
            # Validar que el teléfono no esté registrado
            if Cliente.query.filter_by(telefono=telefono).first():
                flash('El número de teléfono ya está registrado', 'error')
                return redirect(url_for('clientes.nuevo'))
            
            # Validar que el email no esté registrado (si se proporcionó)
            if email and Cliente.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return redirect(url_for('clientes.nuevo'))
            
            # Crear nuevo cliente
            cliente = Cliente(
                nombre=nombre,
                telefono=telefono,
                email=email,
                direccion=direccion,
                notas=notas
            )
            
            db.session.add(cliente)
            db.session.commit()
            
            flash('Cliente registrado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el cliente: {str(e)}', 'error')
            return redirect(url_for('clientes.nuevo'))
    
    return render_template('clientes/nuevo.html')

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Obtener estadísticas del cliente
    ventas_stats = db.session.query(
        func.count(Venta.id).label('total_ventas'),
        func.sum(Venta.total).label('total_gastado')
    ).filter(Venta.cliente_id == id).first()
    
    cliente.total_ventas = ventas_stats.total_ventas or 0
    cliente.total_gastado = ventas_stats.total_gastado or 0
    
    # Licencias activas
    cliente.licencias_activas = Venta.query.filter(
        Venta.cliente_id == id,
        Venta.fecha_expiracion > datetime.now()
    ).count()
    
    if request.method == 'POST':
        try:
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            
            # Validar que el teléfono no esté registrado (excepto el actual)
            telefono_existente = Cliente.query.filter(
                Cliente.telefono == telefono,
                Cliente.id != id
            ).first()
            if telefono_existente:
                flash('El número de teléfono ya está registrado', 'error')
                return redirect(url_for('clientes.editar', id=id))
            
            # Validar que el email no esté registrado (si se proporcionó)
            if email:
                email_existente = Cliente.query.filter(
                    Cliente.email == email,
                    Cliente.id != id
                ).first()
                if email_existente:
                    flash('El email ya está registrado', 'error')
                    return redirect(url_for('clientes.editar', id=id))
            
            # Actualizar datos del cliente
            cliente.nombre = request.form.get('nombre')
            cliente.telefono = telefono
            cliente.email = email
            cliente.direccion = request.form.get('direccion')
            cliente.notas = request.form.get('notas')
            
            db.session.commit()
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('clientes.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el cliente: {str(e)}', 'error')
    
    return render_template('clientes/editar.html', cliente=cliente)

@clientes_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar si el cliente tiene ventas asociadas
    if cliente.ventas:
        flash('No se puede eliminar el cliente porque tiene ventas asociadas', 'error')
        return redirect(url_for('clientes.index'))
    
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el cliente: {str(e)}', 'error')
    
    return redirect(url_for('clientes.index'))

@clientes_bp.route('/detalles/<int:id>')
@login_required
def detalles(id):
    cliente = Cliente.query.get_or_404(id)
    
    # Obtener estadísticas del cliente
    stats = db.session.query(
        func.count(Venta.id).label('total_ventas'),
        func.sum(Venta.total).label('total_gastado'),
        func.avg(Venta.total).label('promedio_compra')
    ).filter(Venta.cliente_id == id).first()
    
    # Obtener licencias activas
    licencias_activas = Venta.query.filter(
        Venta.cliente_id == id,
        Venta.fecha_expiracion > datetime.now()
    ).order_by(Venta.fecha_expiracion).all()
    
    # Obtener últimas ventas
    ultimas_ventas = Venta.query.filter_by(cliente_id=id)\
        .order_by(Venta.fecha_venta.desc())\
        .limit(10).all()
    
    now = datetime.utcnow()
    
    return render_template('clientes/detalles.html',
                         cliente=cliente,
                         stats=stats,
                         licencias_activas=licencias_activas,
                         ultimas_ventas=ultimas_ventas,
                         now=now) 