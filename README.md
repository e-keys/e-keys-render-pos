# E-KEYS POS

Aplicación POS (Point of Sale) en Flask con SQLite. Compatible con despliegue gratuito en Render.

## 🚀 Despliegue en Render

1. Sube el proyecto a un repositorio de GitHub.
2. Entra a https://render.com
3. Crea un nuevo Web Service conectado al repositorio.
4. Usa los siguientes comandos:

**Build command**:
```
pip install -r requirements.txt
```

**Start command**:
```
gunicorn run:app
```

**Python version**: 3.11.0

## ⚙️ Requisitos

- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Flask-Login
- gunicorn 
