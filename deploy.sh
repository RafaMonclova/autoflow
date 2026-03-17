#!/bin/bash

docker compose down --remove-orphans
docker compose build

# Ajusta ownership del volumen de media para ejecución como appuser
docker compose run --rm --user root web sh -c "mkdir -p /app/media; chown -R appuser:appuser /app/media"

docker compose up -d

# Solo si usa websockets con Daphne

# docker exec -it autoflow_celery pip uninstall channels -y
# docker exec -it autoflow_celery pip uninstall daphne -y
# docker exec -it autoflow_celery pip install -U channels["daphne"]
