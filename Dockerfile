# Base Python 3.11 slim
FROM python:3.11-slim

WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    redis-tools \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Requisitos Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

EXPOSE 8000

# CMD mejorado
CMD bash -c "\
  # Esperar PostgreSQL
  until pg_isready -h \$POSTGRES_HOST -p \$POSTGRES_PORT -U \$POSTGRES_USER; do \
    echo 'Esperando PostgreSQL...'; sleep 1; \
  done; \
  # Esperar Redis
  until redis-cli -h \$REDIS_HOST -p \$REDIS_PORT ping | grep -q PONG; do \
    echo 'Esperando Redis...'; sleep 1; \
  done; \
  echo 'Todo listo'; \
  # Solo correr Alembic si no hay migraciones aplicadas
  if [ -z \"\$(alembic current 2>/dev/null | grep 'heads')\" ]; then \
    echo 'Aplicando migraciones iniciales...'; \
    alembic upgrade head; \
  else \
    echo 'Migraciones ya aplicadas'; \
  fi; \
  # Arrancar FastAPI
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
