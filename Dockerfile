# ============================================
# Stage 1: Builder - Instalar dependencias
# ============================================
FROM python:3.11-slim AS builder

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias de build si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias en un directorio específico
COPY requirements.txt .

# Instalar las dependencias en un directorio local
# Usar --no-compile para evitar archivos .pyc innecesarios en el builder
RUN pip install --no-cache-dir --user --no-compile -r requirements.txt \
    && find /root/.local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -type f -name '*.pyc' -delete \
    && find /root/.local -type f -name '*.pyo' -delete

# ============================================
# Stage 2: Runtime - Imagen final optimizada
# ============================================
FROM python:3.11-slim

# Labels para metadatos (buenas prácticas)
LABEL maintainer="ariadna.lopez5@educa.madrid.org" \
      version="1.0" \
      description="FastAPI Web Application"

# Variables de entorno para optimización de Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear un usuario no-root para ejecutar la aplicación
RUN useradd -m -u 1000 fastapi && \
    mkdir -p /app && \
    chown -R fastapi:fastapi /app

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar las dependencias instaladas desde el builder
COPY --from=builder /root/.local /home/fastapi/.local

# Copiar solo los archivos necesarios de la aplicación
# Usar .dockerignore para excluir archivos automáticamente
COPY --chown=fastapi:fastapi main.py .
COPY --chown=fastapi:fastapi encript.py .
COPY --chown=fastapi:fastapi Dockerfile .
COPY --chown=fastapi:fastapi docker-compose.watchtower.yml .
COPY --chown=fastapi:fastapi templates/ ./templates/
COPY --chown=fastapi:fastapi static/ ./static/
COPY --chown=fastapi:fastapi data/ ./data/
COPY --chown=fastapi:fastapi domain/ ./domain/
COPY --chown=fastapi:fastapi router/ ./router/
COPY --chown=fastapi:fastapi utils/ ./utils/
COPY --chown=fastapi:fastapi sql/ ./sql/


# Compilar archivos Python para mejorar el tiempo de inicio
RUN python -m compileall -b /app && \
    find /app -type f -name '*.py' -delete && \
    find /app -type f -name '*.pyc' -exec rename 's/\.pyc$/\.py/' {} \; 2>/dev/null || true

# Cambiar al usuario no-root
USER fastapi

# Agregar el directorio local de pip al PATH
ENV PATH=/home/fastapi/.local/bin:$PATH

# Exponer el puerto 8000
EXPOSE 8000

# Healthcheck más ligero usando uvicorn directamente
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

# Comando para ejecutar la aplicación con opciones optimizadas
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "info"]