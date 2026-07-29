#!/bin/sh
set -e

# One image, three roles — set SERVICE_ROLE per deployment (Railway service, or
# docker-compose's `command:` override for local dev) rather than maintaining
# separate images/Dockerfiles for web/worker/beat.
case "$SERVICE_ROLE" in
  worker)
    exec celery -A config worker -l info
    ;;
  beat)
    exec celery -A config beat -l info
    ;;
  *)
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
    # daphne (ASGI), not gunicorn — Chat's WebSocket consumers need a real ASGI server.
    exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
    ;;
esac
