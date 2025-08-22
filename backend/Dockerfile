ARG PYTHON_VERSION=3.12-slim
ARG NODE_VERSION=18-alpine

# 1) Build frontend
FROM node:${NODE_VERSION} AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# 2) Python runtime image
FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (add build tools if your deps need it)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

###########
# App code
COPY backend/ ./backend/

# Copy built frontend into location Django expects for static collection
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Collect static files (includes frontend build artifacts)
RUN python backend/manage.py collectstatic --noinput

# Entrypoint for production (gunicorn)
COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["/entrypoint.sh"]
