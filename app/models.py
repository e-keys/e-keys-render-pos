from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    nombre = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    direccion = db.Column(db.String(200))
    notas = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ventas = db.relationship('Venta', back_populates='cliente', lazy=True)

class TipoProducto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    productos = db.relationship('Producto', backref='tipo', lazy=True)

    def __repr__(self):
        return f'<TipoProducto {self.nombre}>'

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_producto.id'), nullable=False)
    precio_costo = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    stock_minimo = db.Column(db.Integer, default=5)
    duracion = db.Column(db.Integer, default=30)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    proveedor = db.relationship('Proveedor', back_populates='productos', lazy=True)
    ventas = db.relationship('Venta', back_populates='producto', lazy=True)
    credenciales = db.relationship('CredencialProducto', back_populates='producto', lazy=True)

    def __repr__(self):
        return f'<Producto {self.nombre}>'

    @property
    def stock(self):
        return CredencialProducto.query.filter_by(producto_id=self.id, estado='disponible').count()

    @property
    def credenciales_disponibles(self):
        return CredencialProducto.query.filter_by(producto_id=self.id, estado='disponible').all()

    def validar_precio(self):
        if self.precio_venta < self.precio_costo:
            raise ValueError('El precio de venta no puede ser menor al precio de costo')

    def validar_stock(self):
        if self.stock <= 0:
            raise ValueError('No hay stock disponible')

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo

class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    direccion = db.Column(db.String(200))
    notas = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    productos = db.relationship('Producto', back_populates='proveedor', lazy=True)

    @property
    def productos_sin_stock(self):
        productos = Producto.query.filter_by(proveedor_id=self.id).all()
        return sum(1 for p in productos if p.stock == 0)

    @property
    def productos_stock_bajo(self):
        productos = Producto.query.filter_by(proveedor_id=self.id).all()
        return sum(1 for p in productos if p.stock <= p.stock_minimo and p.stock > 0)

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

class CredencialProducto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    usuario = db.Column(db.String(120))
    contrasena = db.Column(db.String(120))
    estado = db.Column(db.String(20), default='disponible')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_expiracion = db.Column(db.DateTime)
    
    producto = db.relationship('Producto', back_populates='credenciales', lazy=True)
    venta = db.relationship('Venta', back_populates='credencial', uselist=False, lazy=True)

class Venta(db.Model):
    __tablename__ = 'venta'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    credencial_id = db.Column(db.Integer, db.ForeignKey('credencial_producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    descuento = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    canal_venta = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='activo')
    notas = db.Column(db.Text)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_expiracion = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cliente = db.relationship('Cliente', back_populates='ventas', lazy=True)
    producto = db.relationship('Producto', back_populates='ventas', lazy=True)
    credencial = db.relationship('CredencialProducto', back_populates='venta', lazy=True)

    def __init__(self, **kwargs):
        super(Venta, self).__init__(**kwargs)
        if not self.fecha_expiracion and self.producto:
            self.fecha_expiracion = self.fecha_venta + timedelta(days=self.producto.duracion)
        if not self.total:
            self.total = self.calcular_total()
    
    def calcular_total(self):
        subtotal = self.cantidad * self.precio_unitario
        if self.descuento > 0:
            return subtotal * (1 - self.descuento/100)
        return subtotal

    def calcular_ganancia(self):
        if not self.producto:
            return 0
        costo_total = self.producto.precio_costo * self.cantidad
        return self.total - costo_total

    def calcular_dias_restantes(self):
        if not self.fecha_expiracion:
            return 0
        now = datetime.utcnow()
        if self.fecha_expiracion < now:
            return 0
        return (self.fecha_expiracion - now).days

    def obtener_estado(self):
        if self.estado == 'cancelado':
            return 'cancelado'
        if not self.fecha_expiracion:
            return 'activo'
        now = datetime.utcnow()
        if self.fecha_expiracion < now:
            return 'expirado'
        return 'activo'

    def validar_precio(self):
        if self.producto and self.precio_unitario < self.producto.precio_costo:
            raise ValueError('El precio unitario no puede ser menor al precio de costo')

    def validar_stock(self):
        if self.producto and self.cantidad > self.producto.stock:
            raise ValueError('No hay suficiente stock disponible')

def get_licencias_activas():
    now = datetime.now()
    return CredencialProducto.query.filter(
        CredencialProducto.estado == 'vendido',
        db.or_(
            CredencialProducto.fecha_expiracion > now,
            CredencialProducto.fecha_expiracion == None
        )
    ).count()

def get_licencias_por_expirar():
    now = datetime.utcnow()
    return db.session.query(
        CredencialProducto,
        Producto.nombre.label('producto_nombre'),
        Cliente.nombre.label('cliente_nombre'),
        Venta.fecha_expiracion,
        (func.DATE_PART('day', Venta.fecha_expiracion - func.current_date())).label('dias_restantes')
    )\
        .join(Producto, Producto.id == CredencialProducto.producto_id)\
        .join(Venta, Venta.credencial_id == CredencialProducto.id)\
        .join(Cliente, Cliente.id == Venta.cliente_id)\
        .filter(
            CredencialProducto.estado == 'vendido',
            Venta.fecha_expiracion <= now + timedelta(days=30),
            Venta.fecha_expiracion > now
        )\
        .order_by(Venta.fecha_expiracion)\
        .limit(5)\
        .all()
