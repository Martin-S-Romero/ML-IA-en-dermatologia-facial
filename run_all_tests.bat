@echo off
echo ==========================================================
echo     INICIANDO BATERIA COMPLETA DE PRUEBAS - TESIS 2.0     
echo ==========================================================

echo.
echo [+] EJECUTANDO PRUEBAS UNITARIAS DEL SISTEMA...

echo ------------------------------------------------
echo Ejecutando: Autenticacion y Flujo de Usuarios
python scripts/test_auth_flow.py

echo ------------------------------------------------
echo Ejecutando: Rate Limiting
python scripts/test_rate_limit.py

echo ------------------------------------------------
echo Ejecutando: Perfil de Usuario
python scripts/test_users.py

echo ------------------------------------------------
echo Ejecutando: Rutinas de Cuidado
python scripts/test_routines.py

echo ------------------------------------------------
echo Ejecutando: Base de Datos de Productos
python scripts/test_products.py

echo ------------------------------------------------
echo Ejecutando: Modos de Censura IA (Unit Test)
python scripts/test_censorship_modes.py

echo ------------------------------------------------
echo Ejecutando: Pipeline Completo (Subida -^> Redis -^> Celery -^> Polling)
python scripts/test_skin_mock.py

echo.
echo [+] EJECUTANDO PRUEBAS DE SEGURIDAD Y DEFENSA...

echo ------------------------------------------------
echo Ejecutando: Aislamiento CORS
python scripts\attacks\test_cors_isolation.py

echo ------------------------------------------------
echo Ejecutando: Validacion de Security Headers
python scripts\attacks\test_security_headers.py

echo ------------------------------------------------
echo Ejecutando: Aislamiento de Datos por Inquilino (Row-Level Security)
python scripts\attacks\test_rls_isolation.py

echo.
echo ==========================================================
echo          TODAS LAS PRUEBAS HAN FINALIZADO               
echo ==========================================================
pause
