FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear carpeta para logs
RUN mkdir -p logs

# Recolectar estáticos
RUN python manage.py collectstatic --noinput

# --- NUEVO: Configuración del Entrypoint ---

# 1. Copiamos el script
COPY entrypoint.sh /entrypoint.sh

# 2. Le damos permisos de ejecución (CRÍTICO en Linux)
RUN chmod +x /entrypoint.sh

# 3. Definimos el entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# -------------------------------------------

EXPOSE 8000

# El CMD se pasará como argumento ($@) al entrypoint.sh
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "alcaldiaPOA.wsgi:application", "--workers", "2", "--threads", "4"]