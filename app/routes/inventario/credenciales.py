from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import CredencialProducto, Producto
from app import db
from datetime import datetime

credenciales_bp = Blueprint('credenciales', __name__, url_prefix='/credenciales')

@credenciales_bp.route('/')
@login_required
def index():
    # Obtener parámetros de filtro
    producto = request.args.get('producto', '')
    estado = request.args.get('estado', '')
    
    # Construir query base
    query = CredencialProducto.query.join(Producto)
    
    # Aplicar filtros
    if producto:
        query = query.filter(Producto.nombre.ilike(f'%{producto}%'))
    if estado:
        query = query.filter(CredencialProducto.estado == estado)
    
    # Ordenar por fecha de creación descendente
    credenciales = query.order_by(CredencialProducto.fecha_creacion.desc()).all()
    
    # Obtener listas para los filtros
    productos = Producto.query.all()
    estados = ['disponible', 'vendido', 'expirado']
    
    return render_template('inventario/credenciales/index.html',
                         credenciales=credenciales,
                         productos=productos,
                         estados=estados)

@credenciales_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id')
            cantidad = int(request.form.get('cantidad'))
            
            # Validar datos requeridos
            if not all([producto_id, cantidad]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('credenciales.nueva'))
            
            producto = Producto.query.get_or_404(producto_id)
            
            # Crear las credenciales
            for _ in range(cantidad):
                credencial = CredencialProducto(
                    producto_id=producto_id,
                    estado='disponible',
                    fecha_creacion=datetime.utcnow()
                )
                db.session.add(credencial)
            
            # Actualizar stock del producto
            producto.stock += cantidad
            
            db.session.commit()
            flash(f'{cantidad} credenciales creadas exitosamente', 'success')
            return redirect(url_for('credenciales.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear las credenciales: {str(e)}', 'error')
            return redirect(url_for('credenciales.nueva'))
    
    productos = Producto.query.all()
    return render_template('inventario/credenciales/nueva.html',
                         productos=productos)

@credenciales_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    credencial = CredencialProducto.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos
            credencial.usuario = request.form.get('usuario')
            credencial.contrasena = request.form.get('contrasena')
            credencial.estado = request.form.get('estado')
            
            # Actualizar fecha de expiración si se proporciona
            fecha_expiracion = request.form.get('fecha_expiracion')
            if fecha_expiracion:
                credencial.fecha_expiracion = datetime.strptime(fecha_expiracion, '%Y-%m-%d')
            
            db.session.commit()
            flash('Credencial actualizada exitosamente', 'success')
            return redirect(url_for('credenciales.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la credencial: {str(e)}', 'error')
    
    estados = ['disponible', 'vendido', 'expirado']
    return render_template('inventario/credenciales/editar.html',
                         credencial=credencial,
                         estados=estados)

@credenciales_bp.route('/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    credencial = CredencialProducto.query.get_or_404(id)
    try:
        # Solo se pueden eliminar credenciales disponibles
        if credencial.estado != 'disponible':
            raise ValueError('Solo se pueden eliminar credenciales disponibles')
        
        # Actualizar stock del producto
        producto = credencial.producto
        producto.stock -= 1
        
        db.session.delete(credencial)
        db.session.commit()
        flash('Credencial eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la credencial: {str(e)}', 'error')
    
    return redirect(url_for('credenciales.index'))

@credenciales_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id')
            credenciales_texto = request.form.get('credenciales')
            
            # Validar datos requeridos
            if not all([producto_id, credenciales_texto]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('credenciales.importar'))
            
            producto = Producto.query.get_or_404(producto_id)
            
            # Procesar el texto de credenciales (formato: usuario,contraseña\n)
            lineas = credenciales_texto.strip().split('\n')
            credenciales_creadas = 0
            
            for linea in lineas:
                if ',' in linea:
                    usuario, contrasena = linea.strip().split(',', 1)
                    credencial = CredencialProducto(
                        producto_id=producto_id,
                        usuario=usuario.strip(),
                        contrasena=contrasena.strip(),
                        estado='disponible',
                        fecha_creacion=datetime.utcnow()
                    )
                    db.session.add(credencial)
                    credenciales_creadas += 1
            
            # Actualizar stock del producto
            producto.stock += credenciales_creadas
            
            db.session.commit()
            flash(f'{credenciales_creadas} credenciales importadas exitosamente', 'success')
            return redirect(url_for('credenciales.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al importar las credenciales: {str(e)}', 'error')
            return redirect(url_for('credenciales.importar'))
    
    productos = Producto.query.all()
    return render_template('inventario/credenciales/importar.html',
                         productos=productos) 