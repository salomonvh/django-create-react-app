#!/usr/bin/env sh
set -e

# Default port if not provided
export PORT=${PORT:-8000}

# Apply database migrations (SQLite by default)
python backend/manage.py migrate --noinput

# Launch Gunicorn (change workers as needed)
exec gunicorn web.wsgi:application \
  --chdir backend \
  --bind 0.0.0.0:${PORT} \
  --workers ${GUNICORN_WORKERS:-3} \
  --timeout ${GUNICORN_TIMEOUT:-60}

