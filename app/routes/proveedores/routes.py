from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models import Proveedor, Producto
from app import db
from sqlalchemy import func
from app.routes.proveedores import proveedores_bp

@proveedores_bp.route('/')
@login_required
def index():
    # Obtener parámetros de búsqueda
    buscar = request.args.get('buscar', '')
    
    # Construir query base
    query = Proveedor.query
    
    # Aplicar filtro de búsqueda
    if buscar:
        query = query.filter(
            Proveedor.nombre.ilike(f'%{buscar}%') |
            Proveedor.telefono.ilike(f'%{buscar}%') |
            Proveedor.email.ilike(f'%{buscar}%')
        )
    
    # Obtener proveedores con estadísticas
    proveedores = query.order_by(Proveedor.nombre).all()
    
    # Para cada proveedor, obtener estadísticas
    for proveedor in proveedores:
        # Total de productos
        total_productos = db.session.query(
            func.count(Producto.id)
        ).filter(Producto.proveedor_id == proveedor.id).scalar() or 0
        
        # Obtener productos del proveedor
        productos = Producto.query.filter(Producto.proveedor_id == proveedor.id).all()
        
        # Calcular stock total sumando las credenciales disponibles
        total_stock = sum(len(p.credenciales_disponibles) for p in productos)
        
        proveedor.total_productos = total_productos
        proveedor.total_stock = total_stock
    
    return render_template('proveedores/index.html',
                         proveedores=proveedores,
                         buscar=buscar)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
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
            if Proveedor.query.filter_by(telefono=telefono).first():
                flash('El número de teléfono ya está registrado', 'error')
                return redirect(url_for('proveedores.nuevo'))
            
            # Validar que el email no esté registrado (si se proporcionó)
            if email and Proveedor.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return redirect(url_for('proveedores.nuevo'))
            
            # Crear nuevo proveedor
            proveedor = Proveedor(
                nombre=nombre,
                telefono=telefono,
                email=email,
                direccion=direccion,
                notas=notas
            )
            
            db.session.add(proveedor)
            db.session.commit()
            
            flash('Proveedor registrado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el proveedor: {str(e)}', 'error')
            return redirect(url_for('proveedores.nuevo'))
    
    return render_template('proveedores/nuevo.html')

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            
            # Validar que el teléfono no esté registrado (excepto el actual)
            telefono_existente = Proveedor.query.filter(
                Proveedor.telefono == telefono,
                Proveedor.id != id
            ).first()
            if telefono_existente:
                flash('El número de teléfono ya está registrado', 'error')
                return redirect(url_for('proveedores.editar', id=id))
            
            # Validar que el email no esté registrado (si se proporcionó)
            if email:
                email_existente = Proveedor.query.filter(
                    Proveedor.email == email,
                    Proveedor.id != id
                ).first()
                if email_existente:
                    flash('El email ya está registrado', 'error')
                    return redirect(url_for('proveedores.editar', id=id))
            
            # Actualizar datos del proveedor
            proveedor.nombre = request.form.get('nombre')
            proveedor.telefono = telefono
            proveedor.email = email
            proveedor.direccion = request.form.get('direccion')
            proveedor.notas = request.form.get('notas')
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('proveedores.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el proveedor: {str(e)}', 'error')
    
    return render_template('proveedores/editar.html', proveedor=proveedor)

@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    # Verificar si el proveedor tiene productos asociados
    if proveedor.productos:
        flash('No se puede eliminar el proveedor porque tiene productos asociados', 'error')
        return redirect(url_for('proveedores.index'))
    
    try:
        db.session.delete(proveedor)
        db.session.commit()
        flash('Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el proveedor: {str(e)}', 'error')
    
    return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/detalles/<int:id>')
@login_required
def detalles(id):
    proveedor = Proveedor.query.get_or_404(id)
    
    # Obtener productos del proveedor
    productos = Producto.query.filter_by(proveedor_id=id).all()
    
    # Calcular estadísticas
    total_productos = len(productos)
    total_stock = sum(p.stock for p in productos)
    promedio_precio = sum(p.precio_costo for p in productos) / total_productos if total_productos > 0 else 0
    
    # Obtener productos sin stock y con stock bajo
    productos_sin_stock = [p for p in productos if p.stock == 0]
    productos_stock_bajo = [p for p in productos if p.stock <= p.stock_minimo and p.stock > 0]
    
    return render_template('proveedores/detalles.html',
                         proveedor=proveedor,
                         total_productos=total_productos,
                         total_stock=total_stock,
                         promedio_precio=promedio_precio,
                         productos_sin_stock=productos_sin_stock,
                         productos_stock_bajo=productos_stock_bajo,
                         productos=productos) 