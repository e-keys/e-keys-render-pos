@echo off
echo Iniciando sistema POS EKEYS...
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    echo Entorno virtual creado.
)

REM Activar el entorno virtual
call .venv\Scripts\activate.bat

REM Verificar si existen las dependencias
if not exist "requirements.txt" (
    echo Error: No se encuentra el archivo requirements.txt
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install -r requirements.txt

REM Verificar si existe la base de datos
if not exist "instance\pos_ekeys.db" (
    echo Creando base de datos...
    python create_db.py
    echo Base de datos creada.
)

REM Iniciar la aplicación en segundo plano
echo Iniciando la aplicación...
echo.
echo Sistema POS EKEYS iniciado correctamente.
echo Presione Ctrl+C para detener el servidor.
echo.

REM Iniciar la aplicación en segundo plano y esperar 5 segundos para que el servidor esté listo
start /b python run.py
timeout /t 5 /nobreak

REM Abrir Edge con la aplicación
start microsoft-edge:http://127.0.0.1:5000

REM Esperar a que el usuario cierre la ventana
pause

REM Terminar el proceso de Python
taskkill /F /IM python.exe

REM Desactivar el entorno virtual al cerrar
deactivate 