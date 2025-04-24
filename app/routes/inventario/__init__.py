from flask import Blueprint

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')
credenciales_bp = Blueprint('credenciales', __name__, url_prefix='/inventario/credenciales')

from app.routes.inventario import routes, credenciales 