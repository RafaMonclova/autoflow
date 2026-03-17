#!/bin/bash
set -e

# Deshabilitar buffering de Python para ver logs en tiempo real
export PYTHONUNBUFFERED=1

# Solo si se usa websockets con Daphne y Channels

# pip uninstall channels -y
# pip uninstall daphne -y
# pip install -U channels["daphne"]

python manage.py collectstatic --noinput

#exec gunicorn config.wsgi:application --bind 0.0.0.0:5012 -w 2 --timeout 300
# Ejecutar Daphne con verbosity aumentada y sin buffering (solo si se usa websockets con Daphne y Channels)
exec daphne -b 0.0.0.0 -p 5012 -v 2 config.asgi:application
