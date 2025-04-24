from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models import Venta, Cliente, Producto, CredencialProducto
from app import db
from datetime import datetime

ventas = Blueprint('ventas', __name__)

@ventas.route('/')
@login_required
def index():
    # Obtener todas las ventas con sus relaciones
    ventas = Venta.query.join(Cliente).join(Producto).all()
    return render_template('ventas/index.html', ventas=ventas)

@ventas.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        try:
            cliente_id = request.form.get('cliente_id')
            producto_id = request.form.get('producto_id')
            cantidad = int(request.form.get('cantidad'))
            precio_unitario = float(request.form.get('precio_unitario'))
            canal_venta = request.form.get('canal_venta')
            estado = request.form.get('estado')
            notas = request.form.get('notas')
            
            # Verificar stock disponible
            producto = Producto.query.get_or_404(producto_id)
            if producto.stock < cantidad:
                flash('No hay suficiente stock disponible', 'error')
                return redirect(url_for('ventas.nuevo'))
            
            # Obtener una credencial disponible
            credencial = CredencialProducto.query.filter_by(
                producto_id=producto_id,
                estado='disponible'
            ).first()
            
            if not credencial:
                flash('No hay credenciales disponibles para este producto', 'error')
                return redirect(url_for('ventas.nuevo'))
            
            # Crear la venta
            venta = Venta(
                cliente_id=cliente_id,
                producto_id=producto_id,
                credencial_id=credencial.id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                canal_venta=canal_venta,
                estado=estado,
                notas=notas,
                fecha_venta=datetime.now()
            )
            
            # Actualizar estado de la credencial
            credencial.estado = 'vendido'
            
            db.session.add(venta)
            db.session.commit()
            
            flash('Venta creada exitosamente', 'success')
            return redirect(url_for('ventas.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la venta: {str(e)}', 'error')
            return redirect(url_for('ventas.nuevo'))
    
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template('ventas/nuevo.html', clientes=clientes, productos=productos)

@ventas.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    # Obtener la venta con todas sus relaciones
    venta = Venta.query.join(Cliente).join(Producto).join(CredencialProducto).filter(Venta.id == id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Guardar los IDs anteriores para comparar
            old_producto_id = venta.producto_id
            
            # Actualizar datos básicos
            venta.cliente_id = request.form.get('cliente_id')
            venta.producto_id = request.form.get('producto_id')
            venta.cantidad = int(request.form.get('cantidad'))
            venta.precio_unitario = float(request.form.get('precio_unitario'))
            venta.canal_venta = request.form.get('canal_venta')
            venta.estado = request.form.get('estado')
            venta.notas = request.form.get('notas')
            
            # Si cambió el producto, actualizar la credencial
            if old_producto_id != venta.producto_id:
                # Liberar la credencial anterior
                old_credencial = CredencialProducto.query.get(venta.credencial_id)
                if old_credencial:
                    old_credencial.estado = 'disponible'
                
                # Obtener nueva credencial
                new_credencial = CredencialProducto.query.filter_by(
                    producto_id=venta.producto_id,
                    estado='disponible'
                ).first()
                
                if not new_credencial:
                    raise ValueError('No hay credenciales disponibles para el nuevo producto')
                
                venta.credencial_id = new_credencial.id
                new_credencial.estado = 'vendido'
            
            # Recalcular total
            venta.total = venta.cantidad * venta.precio_unitario
            
            db.session.commit()
            flash('Venta actualizada exitosamente', 'success')
            return redirect(url_for('ventas.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la venta: {str(e)}', 'error')
            return redirect(url_for('ventas.editar', id=id))
    
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template('ventas/editar.html', 
                         venta=venta, 
                         clientes=clientes, 
                         productos=productos)

@ventas.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    venta = Venta.query.get_or_404(id)
    
    try:
        # Liberar la credencial asociada
        credencial = CredencialProducto.query.get(venta.credencial_id)
        if credencial:
            credencial.estado = 'disponible'
        
        db.session.delete(venta)
        db.session.commit()
        flash('Venta eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la venta: {str(e)}', 'error')
    
    return redirect(url_for('ventas.index'))

@ventas.route('/api/productos/<int:id>')
@login_required
def get_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'precio_venta': producto.precio_venta,
        'precio_costo': producto.precio_costo,
        'stock': producto.stock
    }) 