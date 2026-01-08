#!/bin/sh

# Si algún comando falla, el script se detiene (para no iniciar con errores)
set -e

echo "--> Aplicando migraciones de base de datos..."
python manage.py migrate

echo "--> Iniciando servidor..."
# Esto ejecuta el comando que tengas en CMD en el Dockerfile (gunicorn)
exec "$@"