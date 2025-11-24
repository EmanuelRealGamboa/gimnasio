# Imagen base
FROM python:3.10-slim

# Config Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo
WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código del proyecto
COPY . .

# Puerto interno
EXPOSE 8000

# IMPORTANTE: reemplaza "gym" por el nombre de TU proyecto (carpeta de settings.py/wsgi.py)
CMD ["gunicorn", "gym.wsgi:application", "--bind", "0.0.0.0:8000"]
