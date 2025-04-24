from sqlalchemy import create_engine, inspect

# Conexiones a SQLite y PostgreSQL
sqlite_engine = create_engine('sqlite:///instance/app.db')
postgres_engine = create_engine('postgresql://ekeysuser:xSvDPJqHeKrsc7CoX85zrfZxV4tG7K1u@dpg-d04s99re5dus738l42bg-a.oregon-postgres.render.com/ekeys')

# Inspectores
sqlite_inspector = inspect(sqlite_engine)
postgres_inspector = inspect(postgres_engine)

# Obtener nombres de tablas
sqlite_tables = sqlite_inspector.get_table_names()
postgres_tables = postgres_inspector.get_table_names()

# Mostrar tablas
print("📦 Tablas en SQLite:")
for table in sqlite_tables:
    print(f" - {table}")

print("\n🛢️ Tablas en PostgreSQL:")
for table in postgres_tables:
    print(f" - {table}")

# Comparación
print("\n🔍 Comparación:")

for table in sqlite_tables:
    if table in postgres_tables:
        print(f"✅ {table} existe en ambas bases")
    else:
        print(f"⚠️ {table} existe en SQLite pero NO en PostgreSQL")

for table in postgres_tables:
    if table not in sqlite_tables:
        print(f"⚠️ {table} existe en PostgreSQL pero NO en SQLite")
