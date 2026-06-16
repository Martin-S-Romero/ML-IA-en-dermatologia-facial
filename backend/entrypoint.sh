#!/bin/sh
set -e

echo "================================================"
echo "  SkinAI — Inicializando contenedor backend"
echo "================================================"

echo ""
echo "⏳ Aplicando migraciones de base de datos..."
alembic upgrade head
echo "✅ Migraciones aplicadas"

echo ""
echo "🌱 Ejecutando seed de datos iniciales..."
python /app/scripts/seed_startup.py

echo ""
echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
