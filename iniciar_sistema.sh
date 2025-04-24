#!/bin/bash

echo "Iniciando sistema POS EKEYS..."
echo

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
    echo "Entorno virtual creado."
fi

# Activar el entorno virtual
source .venv/bin/activate

# Verificar si existen las dependencias
if [ ! -f "requirements.txt" ]; then
    echo "Error: No se encuentra el archivo requirements.txt"
    exit 1
fi

# Instalar dependencias si es necesario
echo "Verificando dependencias..."
pip install -r requirements.txt

# Verificar si existe la base de datos
if [ ! -f "instance/pos_ekeys.db" ]; then
    echo "Creando base de datos..."
    python create_db.py
    echo "Base de datos creada."
fi

# Iniciar la aplicación en segundo plano
echo "Iniciando la aplicación..."
echo
echo "Sistema POS EKEYS iniciado correctamente."
echo "Presione Ctrl+C para detener el servidor."
echo

# Iniciar la aplicación en segundo plano
python run.py &
SERVER_PID=$!

# Esperar 5 segundos para que el servidor esté listo
sleep 5

# Abrir el navegador predeterminado
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://127.0.0.1:5000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://127.0.0.1:5000
fi

# Esperar a que el usuario presione Ctrl+C
trap "kill $SERVER_PID; deactivate; exit" INT
wait $SERVER_PID 