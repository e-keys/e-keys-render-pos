# 🚀 SCRIPT DE MIGRACIÓN DE SQLite A PostgreSQL

# 📌 PASO 1: Instala dependencias (si no las tienes ya)
# Ejecuta en tu terminal:
# pip install sqlalchemy psycopg2-binary

# 📌 PASO 2: Guarda este script en un archivo llamado `migrar_sqlite_a_postgres.py`

# 📌 PASO 3: Asegúrate de tener el archivo `app.db` en la misma carpeta que este script

# 📌 PASO 4: Ejecuta el script con:
# python migrar_sqlite_a_postgres.py

from sqlalchemy import create_engine, MetaData

# 🧩 URL de origen (SQLite)
sqlite_url = 'sqlite:///instance/app.db'


# 🧩 URL de destino (PostgreSQL de Render)
postgres_url = 'postgresql://ekeysuser:xSvDPJqHeKrsc7CoX85zrfZxV4tG7K1u@dpg-d04s99re5dus738l42bg-a.oregon-postgres.render.com/ekeys'

# Crear motores de conexión
engine_sqlite = create_engine(sqlite_url)
engine_postgres = create_engine(postgres_url)

# Reflejar la estructura de SQLite
metadata = MetaData()
metadata.reflect(bind=engine_sqlite)

# Crear todas las tablas en PostgreSQL
metadata.create_all(bind=engine_postgres)

# 🔄 Transferencia de datos tabla por tabla
with engine_sqlite.connect() as conn_sqlite, engine_postgres.connect() as conn_postgres:
    for table in metadata.sorted_tables:
        print(f"→ Migrando tabla: {table.name}")
        rows = conn_sqlite.execute(table.select()).fetchall()
        if rows:
            conn_postgres.execute(table.insert(), rows)
        print(f"   ✔ {len(rows)} registros migrados")

print("✅ Migración completada.")
