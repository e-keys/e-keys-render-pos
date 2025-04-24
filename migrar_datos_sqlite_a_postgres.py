# 🚀 MIGRAR SOLO LOS DATOS DE SQLite A POSTGRESQL

# Requisitos:
# pip install sqlalchemy psycopg2-binary

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

# Conexiones a base de datos
sqlite_engine = create_engine('sqlite:///instance/app.db')
postgres_engine = create_engine('postgresql://ekeysuser:xSvDPJqHeKrsc7CoX85zrfZxV4tG7K1u@dpg-d04s99re5dus738l42bg-a.oregon-postgres.render.com/ekeys')

# Sesiones
SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)
sqlite_session = SQLiteSession()
postgres_session = PostgresSession()

# Cargar metadatos desde SQLite
sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)

# Cargar metadatos desde PostgreSQL
postgres_metadata = MetaData()
postgres_metadata.reflect(bind=postgres_engine)

for table_name in sqlite_metadata.tables:
    if table_name in postgres_metadata.tables:
        print(f"→ Migrando tabla: {table_name}")
        source_table = Table(table_name, sqlite_metadata, autoload_with=sqlite_engine)
        dest_table = Table(table_name, postgres_metadata, autoload_with=postgres_engine)

        rows = sqlite_session.execute(source_table.select()).fetchall()
        if rows:
            # Insertar en PostgreSQL
            postgres_session.execute(dest_table.insert(), [dict(row) for row in rows])
            postgres_session.commit()
            print(f"   ✔ {len(rows)} registros migrados")

print("✅ Migración de datos completada.")
