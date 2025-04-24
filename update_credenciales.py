from app import create_app, db
from app.models import CredencialProducto
from datetime import datetime

def update_credenciales():
    app = create_app()
    with app.app_context():
        try:
            # Obtener credenciales con estado 'activa'
            credenciales = CredencialProducto.query.filter_by(estado='activa').all()
            print(f'Credenciales con estado activa: {len(credenciales)}')
            
            # Actualizar estado a 'vendido'
            for credencial in credenciales:
                credencial.estado = 'vendido'
            
            # Guardar cambios
            db.session.commit()
            print('Credenciales actualizadas exitosamente')
            
            # Verificar credenciales expiradas
            now = datetime.now()
            credenciales_expiradas = CredencialProducto.query.filter(
                CredencialProducto.estado == 'vendido',
                CredencialProducto.fecha_expiracion <= now
            ).all()
            
            # Actualizar estado a 'expirado'
            for credencial in credenciales_expiradas:
                credencial.estado = 'expirado'
            
            # Guardar cambios
            db.session.commit()
            print(f'Credenciales expiradas actualizadas: {len(credenciales_expiradas)}')
            
            # Mostrar resumen
            disponibles = CredencialProducto.query.filter_by(estado='disponible').count()
            vendidas = CredencialProducto.query.filter_by(estado='vendido').count()
            expiradas = CredencialProducto.query.filter_by(estado='expirado').count()
            
            print('\nResumen de credenciales:')
            print(f'- Disponibles: {disponibles}')
            print(f'- Vendidas: {vendidas}')
            print(f'- Expiradas: {expiradas}')
            
        except Exception as e:
            print(f'Error al actualizar credenciales: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    update_credenciales() 