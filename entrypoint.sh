#!/bin/sh
set -e

echo "=== Railway Entrypoint ==="
echo "PORT=${PORT:-8000}"
echo "DEBUG=${DEBUG:-not set}"
echo "DATABASE_URL is $([ -n "$DATABASE_URL" ] && echo 'SET' || echo 'NOT SET')"
echo "REDIS_URL is $([ -n "$REDIS_URL" ] && echo 'SET' || echo 'NOT SET')"
echo "SECRET_KEY is $([ -n "$SECRET_KEY" ] && echo 'SET' || echo 'NOT SET')"

# Run migrations (best-effort — don't block startup if DB isn't ready yet)
echo "--- Running migrations ---"
python manage.py migrate --noinput 2>&1 || echo "WARNING: migrate failed (DB may not be provisioned yet)"

# Collect static files
echo "--- Collecting static files ---"
python manage.py collectstatic --noinput 2>&1 || echo "WARNING: collectstatic failed"

echo "--- Starting Daphne on port ${PORT:-8000} ---"
exec daphne -b 0.0.0.0 -p "${PORT:-8000}" config.asgi:application
