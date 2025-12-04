# Guía de Despliegue en Render

Esta guía te ayudará a desplegar tu aplicación Django en Render.com.

## Prerrequisitos

1.  Asegúrate de que tu código esté actualizado en GitHub (ya lo hemos hecho).
2.  Tener una cuenta en [Render.com](https://render.com/).

## Opción 1: Despliegue Automático (Recomendado - Blueprints)

Hemos creado un archivo `render.yaml` que configura todo automáticamente.

1.  En el Dashboard de Render, haz clic en **"New +"** y selecciona **"Blueprint"**.
2.  Conecta tu cuenta de GitHub si aún no lo has hecho.
3.  Selecciona tu repositorio: `sistema_de_poa`.
4.  Dale un nombre al servicio (Service Group Name), por ejemplo: `sistema-poa-prod`.
5.  Haz clic en **"Apply"**.

Render detectará el archivo `render.yaml` y creará automáticamente:
*   Una base de datos PostgreSQL (`sistema_poa_db`).
*   El servicio web (`sistema_poa`) configurado para usar Python, ejecutar el script de construcción y arrancar con Gunicorn.
*   Las variables de entorno necesarias (`DATABASE_URL`, `SECRET_KEY`).

## Opción 2: Despliegue Manual

Si prefieres configurar todo manualmente:

### 1. Crear Base de Datos
1.  En Render, **New +** -> **PostgreSQL**.
2.  Nombre: `sistema_poa_db`.
3.  Database: `sistema_poa`.
4.  User: `sistema_poa_user`.
5.  Region: Elige la más cercana (ej. Oregon).
6.  Plan: Free (o el que prefieras).
7.  **Create Database**.
8.  Copia la **"Internal Database URL"** cuando esté lista.

### 2. Crear Web Service
1.  En Render, **New +** -> **Web Service**.
2.  Conecta tu repositorio `sistema_de_poa`.
3.  **Name**: `sistema-poa`.
4.  **Region**: La misma que la base de datos.
5.  **Branch**: `main`.
6.  **Root Directory**: (Déjalo vacío).
7.  **Runtime**: `Python 3`.
8.  **Build Command**: `./build.sh`
9.  **Start Command**: `gunicorn alcaldiaPOA.wsgi:application`
10. **Plan**: Free.

### 3. Configurar Variables de Entorno
En la sección **Environment** del Web Service, añade:

*   `DATABASE_URL`: (Pega la Internal Database URL que copiaste).
*   `SECRET_KEY`: Genera una clave segura y pégala aquí.
*   `PYTHON_VERSION`: `3.11.0` (o la versión que prefieras, opcional).

### 4. Desplegar
Haz clic en **Create Web Service**. Render comenzará a construir tu aplicación. Puedes ver el progreso en la pestaña "Logs".

## Notas Importantes

*   **Superusuario**: Una vez desplegado, necesitarás crear un superusuario para acceder al admin.
    *   En el dashboard de tu Web Service en Render, ve a la pestaña **"Shell"**.
    *   Ejecuta: `python manage.py createsuperuser` y sigue las instrucciones.
*   **Archivos Estáticos**: La configuración ya incluye `WhiteNoise` para servir los archivos estáticos eficientemente.
*   **Base de Datos**: La configuración usa `dj-database-url` para conectarse automáticamente a la base de datos de Render cuando detecta la variable `DATABASE_URL`. En local seguirá usando SQLite.
