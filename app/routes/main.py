from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import (
    Venta, Producto, Cliente, CredencialProducto,
    get_licencias_activas, get_licencias_por_expirar
)
from datetime import datetime, timedelta
from sqlalchemy import func, extract, desc, asc
from app import db

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    # Obtener todas las ventas para estadísticas globales
    ventas = Venta.query.all()
    
    # Calcular estadísticas globales
    ventas_totales = sum(venta.cantidad for venta in ventas)
    ingresos_totales = sum(venta.cantidad * venta.precio_unitario for venta in ventas)
    ganancia_total = sum(
        venta.cantidad * (venta.precio_unitario - venta.producto.precio_costo)
        for venta in ventas
    )
    
    # Obtener licencias activas
    licencias_activas = get_licencias_activas()
    
    # Datos históricos por mes (desde enero 2025)
    fecha_inicio = datetime(2025, 1, 1)
    meses = []
    ingresos_mensuales = []
    ganancias_mensuales = []
    
    for i in range(12):  # 12 meses desde enero 2025
        fecha = fecha_inicio + timedelta(days=30*i)
        ventas_mes = Venta.query.filter(
            extract('year', Venta.fecha_venta) == fecha.year,
            extract('month', Venta.fecha_venta) == fecha.month
        ).all()
        
        ingresos_mes = sum(v.cantidad * v.precio_unitario for v in ventas_mes)
        ganancia_mes = sum(v.cantidad * (v.precio_unitario - v.producto.precio_costo) for v in ventas_mes)
        
        meses.append(fecha.strftime('%B %Y'))
        ingresos_mensuales.append(ingresos_mes)
        ganancias_mensuales.append(ganancia_mes)
    
    # Obtener datos de productos más vendidos
    productos_vendidos = db.session.query(
        Producto.nombre,
        func.sum(Venta.cantidad).label('total_vendido')
    ).join(Venta).group_by(Producto.id).order_by(
        desc(func.sum(Venta.cantidad))
    ).limit(5).all()
    
    productos_labels = [p[0] for p in productos_vendidos]
    productos_data = [float(p[1]) for p in productos_vendidos]
    
    # Obtener datos de canales de venta
    canales_venta = db.session.query(
        Venta.canal_venta,
        func.count(Venta.id).label('total')
    ).group_by(Venta.canal_venta).all()
    
    canales_labels = [c[0] for c in canales_venta]
    canales_data = [float(c[1]) for c in canales_venta]
    
    # Obtener datos de productos disponibles
    productos_disponibles = db.session.query(
        Producto.nombre,
        func.count(CredencialProducto.id).label('disponibles')
    ).join(
        CredencialProducto,
        db.and_(
            CredencialProducto.producto_id == Producto.id,
            CredencialProducto.estado == 'disponible'
        ),
        isouter=True
    ).group_by(Producto.id).all()
    
    productos_disp_labels = [p[0] for p in productos_disponibles]
    productos_disp_data = [float(p[1]) for p in productos_disponibles]
    
    # Obtener licencias por expirar
    licencias_por_expirar = get_licencias_por_expirar()
    
    # Obtener productos con stock bajo
    productos_stock_bajo = db.session.query(
        Producto,
        func.count(CredencialProducto.id).label('stock_actual')
    ).outerjoin(
        CredencialProducto,
        db.and_(
            CredencialProducto.producto_id == Producto.id,
            CredencialProducto.estado == 'disponible'
        )
    ).group_by(Producto.id).having(
        func.count(CredencialProducto.id) <= Producto.stock_minimo * 2
    ).order_by(
        func.count(CredencialProducto.id)
    ).limit(5).all()
    
    # Extraer solo los productos de la consulta
    productos_stock_bajo = [p[0] for p in productos_stock_bajo]
    
    return render_template('main/index.html',
        ventas_totales=ventas_totales,
        ingresos_totales=ingresos_totales,
        ganancia_total=ganancia_total,
        licencias_activas=licencias_activas,
        productos_labels=productos_labels,
        productos_data=productos_data,
        canales_labels=canales_labels,
        canales_data=canales_data,
        licencias_por_expirar=licencias_por_expirar,
        productos_stock_bajo=productos_stock_bajo,
        meses=meses,
        ingresos_mensuales=ingresos_mensuales,
        ganancias_mensuales=ganancias_mensuales,
        productos_disp_labels=productos_disp_labels,
        productos_disp_data=productos_disp_data,
        now=datetime.now()
    ) 