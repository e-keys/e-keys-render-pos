from sqlalchemy import create_engine, inspect

engine = create_engine('sqlite:///instance/app.db')
inspector = inspect(engine)

tables = inspector.get_table_names()

if tables:
    print("📄 Tablas en instance/app.db:")
    for table in tables:
        print(f" - {table}")
else:
    print("⚠️ No se encontraron tablas en app.db")
