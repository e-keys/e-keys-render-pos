import os
from datetime import timedelta

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Configuración de la base de datos
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{os.path.join(INSTANCE_DIR, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Configuración de la aplicación
    APP_NAME = os.environ.get('APP_NAME') or "E-KEYS Sistema de Gestión"
    COMPANY_NAME = os.environ.get('COMPANY_NAME') or "E-KEYS"
    VERSION = os.environ.get('VERSION') or "1.0.0"
    
    # Configuración de seguridad
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False 

    # 🟢 Confirmación de sincronización con GitHub - Ángel
