from flask import Blueprint

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

from app.routes.ventas import routes 