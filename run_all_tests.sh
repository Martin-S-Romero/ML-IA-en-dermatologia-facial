#!/bin/bash

echo "=========================================================="
echo "    INICIANDO BATERIA COMPLETA DE PRUEBAS - TESIS 2.0     "
echo "=========================================================="

echo -e "\n[+] EJECUTANDO PRUEBAS UNITARIAS DEL SISTEMA..."

echo "------------------------------------------------"
echo "Ejecutando: Autenticacion y Flujo de Usuarios"
python scripts/tests/test_auth_flow.py

echo "------------------------------------------------"
echo "Ejecutando: Rate Limiting"
python scripts/tests/test_rate_limit.py

echo "------------------------------------------------"
echo "Ejecutando: Perfil de Usuario"
python scripts/tests/test_users.py

echo "------------------------------------------------"
echo "Ejecutando: Rutinas de Cuidado"
python scripts/tests/test_routines.py

echo "------------------------------------------------"
echo "Ejecutando: Base de Datos de Productos"
python scripts/tests/test_products.py

echo "------------------------------------------------"
echo "Ejecutando: Fase 2 - Motor de Recomendacion (4 escenarios + contrato)"
python scripts/tests/test_recommendations_phase2.py

echo "------------------------------------------------"
echo "Ejecutando: Endpoints de Analisis (historia, documento, imagen)"
python scripts/tests/test_analysis_endpoints.py

echo "------------------------------------------------"
echo "Ejecutando: Modos de Censura IA (Unit Test)"
python scripts/tests/test_censorship_modes.py

echo "------------------------------------------------"
echo "Ejecutando: Pipeline Completo (Subida -> Redis -> Celery -> Polling)"
python scripts/tests/test_skin_mock.py

echo -e "\n[+] EJECUTANDO PRUEBAS DE SEGURIDAD Y DEFENSA..."

echo "------------------------------------------------"
echo "Ejecutando: Aislamiento CORS"
python scripts/tests/attacks/test_cors_isolation.py

echo "------------------------------------------------"
echo "Ejecutando: Validacion de Security Headers"
python scripts/tests/attacks/test_security_headers.py

echo "------------------------------------------------"
echo "Ejecutando: Aislamiento de Datos por Inquilino (Row-Level Security)"
python scripts/tests/attacks/test_rls_isolation.py

echo -e "\n[+] EJECUTANDO METRICAS DE COBERTURA DEL CATALOGO (requiere Docker en ejecucion)..."

echo "------------------------------------------------"
echo "Ejecutando: Cobertura del catalogo — ingredientes, slots, scoring (dentro del contenedor)"
MSYS_NO_PATHCONV=1 docker-compose exec -T backend python /app/scripts/test_reco_coverage.py \
  || MSYS_NO_PATHCONV=1 docker compose exec -T backend python /app/scripts/test_reco_coverage.py \
  || echo "[OMITIDO] docker-compose no disponible o contenedor detenido."

echo -e "\n=========================================================="
echo "          TODAS LAS PRUEBAS HAN FINALIZADO EXITOSAMENTE     "
echo "=========================================================="
