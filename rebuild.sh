#!/bin/bash

set -e  # Detener el script si ocurre un error

COMPOSE_FILE="docker-compose.yml"

echo "🔻 Bajando contenedores..."
docker compose -f $COMPOSE_FILE down

echo "🗑 Eliminando imágenes asociadas al compose..."
# Obtiene los IDs de imágenes usadas por el compose
IMAGES=$(docker compose -f $COMPOSE_FILE config | grep 'image:' | awk '{print $2}')

for IMAGE in $IMAGES; do
    echo "Eliminando imagen: $IMAGE"
    docker rmi -f $IMAGE || true
done

echo "🚀 Levantando nuevamente los contenedores..."
docker compose -f $COMPOSE_FILE up --build -d

echo "✅ Proceso completado correctamente."


# docker compose -f docker-compose.yml down --rmi all
# docker compose -f docker-compose.yml up --build -d