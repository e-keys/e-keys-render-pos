# ✅ SCRIPT PARA VERIFICAR TABLAS MIGRADAS EN POSTGRESQL

# 📌 Ejecuta en tu terminal:
# pip install sqlalchemy psycopg2-binary

# 📌 Guarda este archivo como `verificar_postgres.py`
# 📌 Ejecuta con:
# python verificar_postgres.py

from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError

# URL de conexión a PostgreSQL en Render
postgres_url = 'postgresql://ekeysuser:xSvDPJqHeKrsc7CoX85zrfZxV4tG7K1u@dpg-d04s99re5dus738l42bg-a.oregon-postgres.render.com/ekeys'

try:
    engine = create_engine(postgres_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    with engine.connect() as conn:
        print("📊 Conteo de registros por tabla:")
        for table in metadata.sorted_tables:
            count = conn.execute(table.count()).scalar()
            print(f"🔹 {table.name}: {count} registros")

except SQLAlchemyError as e:
    print("❌ Error al conectarse a la base de datos:", str(e))
