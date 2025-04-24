from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import TipoProducto
from app import db

tipos_producto_bp = Blueprint('tipos_producto', __name__, url_prefix='/tipos-producto')

@tipos_producto_bp.route('/')
@login_required
def index():
    tipos = TipoProducto.query.all()
    return render_template('tipos_producto/index.html', tipos=tipos)

@tipos_producto_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre es requerido', 'error')
            return redirect(url_for('tipos_producto.nuevo'))
            
        tipo = TipoProducto(nombre=nombre, descripcion=descripcion)
        db.session.add(tipo)
        
        try:
            db.session.commit()
            flash('Tipo de producto creado exitosamente', 'success')
            return redirect(url_for('tipos_producto.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el tipo de producto', 'error')
            return redirect(url_for('tipos_producto.nuevo'))
            
    return render_template('tipos_producto/nuevo.html')

@tipos_producto_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    tipo = TipoProducto.query.get_or_404(id)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        if not nombre:
            flash('El nombre es requerido', 'error')
            return redirect(url_for('tipos_producto.editar', id=id))
            
        tipo.nombre = nombre
        tipo.descripcion = descripcion
        
        try:
            db.session.commit()
            flash('Tipo de producto actualizado exitosamente', 'success')
            return redirect(url_for('tipos_producto.index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el tipo de producto', 'error')
            return redirect(url_for('tipos_producto.editar', id=id))
            
    return render_template('tipos_producto/editar.html', tipo=tipo)

@tipos_producto_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    tipo = TipoProducto.query.get_or_404(id)
    
    if tipo.productos:
        flash('No se puede eliminar un tipo de producto que tiene productos asociados', 'error')
        return redirect(url_for('tipos_producto.index'))
        
    try:
        db.session.delete(tipo)
        db.session.commit()
        flash('Tipo de producto eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el tipo de producto', 'error')
        
    return redirect(url_for('tipos_producto.index')) 