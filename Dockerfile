# Imagen liviana de Python
FROM python:3.12-slim

# Evita archivos .pyc y fuerza salida de logs sin buffer (útil para ver logs en docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias primero (aprovecha la cache de capas de Docker:
# si solo cambia el código fuente, no se reinstalan las dependencias)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación (la carpeta uat/ es solo para
# pruebas manuales locales, no hace falta dentro de la imagen)
COPY app/ ./app/

# Directorio de datos (SQLite / JSON store), montado como volumen en docker-compose
RUN mkdir -p /app/data

# Backend de almacenamiento por defecto (se puede sobreescribir en runtime)
ENV STORAGE_MODE=sqlite
# Puerto por defecto; los hostings tipo Render inyectan su propio $PORT en runtime
ENV PORT=8000

EXPOSE 8000

# Healthcheck simple usando el endpoint /health de la propia API
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",8000)}/health')" || exit 1

# Forma "shell" del CMD para poder interpolar $PORT en runtime
# (Render, Railway y otros hostings inyectan su propio valor de PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
