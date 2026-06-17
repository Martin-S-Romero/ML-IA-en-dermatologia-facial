# Análisis de Seguridad - SkinAI

**Fecha de auditoría:** Mayo 2026  
**Auditor:** Agente de Auditoría Técnica  
**Proyecto:** SkinAI - Plataforma Web de Análisis Cutáneo Asistido por IA

---

## 1. Variables Sensibles Expuestas

### Hallazgo #1: SECRET_KEY Hardcodeado (CRÍTICO)

**Severidad:** Crítica  
**Archivo:** `backend/app/core/security.py` línea 7  
**Evidencia:**
```python
SECRET_KEY = "tesis-secret-key-change-me-in-production"
```

**Impacto:**
- Cualquier persona con acceso al código puede falsificar tokens JWT
- Permite impersonación de usuarios
- Compromete toda la seguridad de autenticación

**Recomendación:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
```

**Prioridad:** Crítica - Debe corregirse antes de cualquier deployment en producción

---

### Hallazgo #2: Credenciales de Base de Datos Hardcodeadas (CRÍTICO)

**Severidad:** Crítica  
**Archivo:** `docker-compose.yml` líneas 13, 33, 58-59  
**Evidencia:**
```yaml
DATABASE_URL=postgresql://app_user:app_password@db:5432/tesis_db
POSTGRES_PASSWORD=password
```

**Impacto:**
- Credenciales expuestas en control de versiones
- Cualquier persona con acceso al repo puede acceder a la base de datos
- Riesgo de robo de datos de usuarios (PII)

**Recomendación:**
```yaml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - POSTGRES_USER=${POSTGRES_USER}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

Crear archivo `.env` (en `.gitignore`):
```
DATABASE_URL=postgresql://app_user:secure_password@db:5432/tesis_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_random_password_here
```

**Prioridad:** Crítica - Debe corregirse inmediatamente

---

### Hallazgo #3: Credenciales en Worker (ALTA)

**Severidad:** Alta  
**Archivo:** `backend/app/worker/tasks.py` línea 15  
**Evidencia:**
```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/tesis_db")
```

**Impacto:**
- Fallback a credenciales hardcodeadas si no hay variable de entorno
- Mismo riesgo que Hallazgo #2

**Recomendación:**
```python
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")
```

**Prioridad:** Alta

---

## 2. Configuraciones Inseguras

### Hallazgo #4: CORS Permisivo (MEDIA)

**Severidad:** Media  
**Archivo:** `backend/app/main.py` líneas 40-48  
**Evidencia:**
```python
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],  # ← Permisivo
)
```

**Impacto:**
- `allow_headers=["*"]` permite cualquier header
- En desarrollo es aceptable, pero en producción debería ser más restrictivo

**Recomendación:**
```python
allow_headers=[
    "Authorization",
    "Content-Type",
    "X-Requested-With"
]
```

**Prioridad:** Media

---

### Hallazgo #5: Rate Limiting Básico (BAJA)

**Severidad:** Baja  
**Archivo:** `backend/app/core/ratelimit.py`  
**Evidencia:**
```python
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
```

**Impacto:**
- Rate limiting por IP (60 req/min) es básico
- No hay rate limiting por usuario
- Vulnerable a ataques distribuidos

**Recomendación:**
- Implementar rate limiting por usuario (usando JWT)
- Considerar Redis-backed rate limiting para distribuido
- Agregar rate limiting más estricto para endpoints sensibles (login, register)

**Prioridad:** Baja

---

## 3. Gestión de Credenciales

### Estado Actual

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Variables de entorno | ⚠️ Parcial | Existe `.env.example` pero no se usa consistentemente |
| .gitignore | ✅ Bien | `.env` está en .gitignore |
| Secrets en commits | ❌ Crítico | SECRET_KEY y contraseñas en commits |
| Rotación de secrets | ❌ No implementado | No hay política de rotación |
| Gestión de secrets | ❌ Manual | No hay vault o gestor de secrets |

### Recomendaciones

1. **Implementar gestor de secrets:**
   - Usar AWS Secrets Manager, HashiCorp Vault, o similar
   - O al mínimo, usar variables de entorno consistentemente

2. **Rotación de secrets:**
   - Establecer política de rotación periódica (ej: cada 90 días)
   - Implementar rotación sin downtime

3. **Auditoría de secrets:**
   - Usar herramientas como `git-secrets` o `truffleHog` para prevenir commits de secrets
   - Revisar historial de git para secrets expuestos

---

## 4. Logs Sensibles

### Hallazgo #6: Logs Potencialmente Sensibles (BAJA)

**Severidad:** Baja  
**Archivo:** `backend/app/core/logger.py`  
**Evidencia:**
```python
logger.info(f"New user registered: {new_user.email}")
logger.info(f"User logged in: {db_user.email}")
```

**Impacto:**
- Logs contienen emails de usuarios (PII)
- Si logs son accesibles, comprometen privacidad

**Recomendación:**
```python
logger.info(f"New user registered: {mask_email(new_user.email)}")
logger.info(f"User logged in: {mask_email(db_user.email)}")

def mask_email(email):
    return email[:3] + "***@" + email.split("@")[1]
```

**Prioridad:** Baja

---

## 5. Seguridad de Base de Datos

### Estado Actual

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Row-Level Security (RLS) | ✅ Implementado | RLS configurado en tablas de usuario |
| Usuario de aplicación | ⚠️ Riesgoso | `app_user` con contraseña débil |
| Conexión SSL | ❌ No configurado | No hay SSL en conexión DB |
| Backups | ❌ No documentado | No hay política de backups |
| Encriptación en reposo | ❌ No implementado | Datos no encriptados en DB |

### Hallazgo #7: Contraseña de Usuario de Aplicación Débil (MEDIA)

**Severidad:** Media  
**Archivo:** `docker-compose.yml` línea 13  
**Evidencia:**
```yaml
DATABASE_URL=postgresql://app_user:app_password@db:5432/tesis_db
```

**Impacto:**
- Contraseña `app_password` es débil y predecible
- Si el contenedor es comprometido, attacker puede acceder a DB

**Recomendación:**
- Usar contraseña fuerte generada aleatoriamente
- Rotar contraseñas periódicamente
- Considerar autenticación por certificado SSL

**Prioridad:** Media

---

## 6. Seguridad de API

### Estado Actual

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Autenticación JWT | ✅ Implementado | JWT con expiración 30 min |
| Refresh tokens | ❌ No implementado | No hay refresh tokens |
| HTTPS | ❌ No configurado | Solo HTTP en desarrollo |
| Input validation | ✅ Implementado | Pydantic schemas |
| Output sanitization | ✅ Implementado | Pydantic schemas |
| SQL Injection | ✅ Protegido | SQLAlchemy ORM protege |
| XSS | ✅ Protegido | Security headers implementados |
| CSRF | ⚠️ Parcial | JWT stateless reduce riesgo, pero no hay tokens CSRF |

### Hallazgo #8: No Hay Refresh Tokens (MEDIA)

**Severidad:** Media  
**Archivo:** `backend/app/core/security.py`  
**Evidencia:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

**Impacto:**
- Usuarios deben re-autenticarse cada 30 minutos
- Mala UX
- En móvil es problemático

**Recomendación:**
- Implementar refresh tokens
- Almacenar refresh tokens en DB con expiración más larga (ej: 7 días)
- Implementar revocación de refresh tokens

**Prioridad:** Media

---

## 7. Seguridad de Infraestructura

### Estado Actual

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Docker containers | ✅ Bien | Contenedores aislados |
| Network isolation | ✅ Bien | Red Docker interna `tesis-network` |
| Exposición de puertos | ⚠️ Aceptable | Puertos expuestos solo en desarrollo |
| Health checks | ✅ Implementado | Health check de DB configurado |
| Image scanning | ❌ No implementado | No hay scanning de vulnerabilidades |
| Runtime security | ❌ No implementado | No hay policies de runtime |

### Hallazgo #9: Puertos Expuestos en Docker Compose (BAJA)

**Severidad:** Baja  
**Archivo:** `docker-compose.yml`  
**Evidencia:**
```yaml
ports:
  - "8000:8000"  # Backend
  - "6379:6379"  # Redis
  - "5432:5432"  # PostgreSQL
  - "3000:3000"  # Frontend
```

**Impacto:**
- En desarrollo es aceptable
- En producción, Redis y PostgreSQL no deberían estar expuestos públicamente

**Recomendación:**
- En producción, no exponer puertos de DB y Redis
- Usar Docker Swarm/Kubernetes con networking interno
- Implementar firewall rules

**Prioridad:** Baja (solo para producción)

---

## 8. Pruebas de Seguridad

### Estado Actual

| Prueba | Estado | Archivo |
|--------|--------|---------|
| Security Headers | ✅ Implementado | `scripts/attacks/test_security_headers.py` |
| CORS Isolation | ✅ Implementado | `scripts/attacks/test_cors_isolation.py` |
| RLS Isolation | ✅ Implementado | `scripts/attacks/test_rls_isolation.py` |
| SQL Injection | ⚠️ No explícito | No hay test específico |
| XSS | ⚠️ No explícito | No hay test específico |
| CSRF | ⚠️ No explícito | No hay test específico |

### Hallazgo #10: Faltan Pruebas de Seguridad Comunes (MEDIA)

**Severidad:** Media  
**Evidencia:** No hay pruebas para:
- SQL Injection
- XSS
- CSRF
- Path traversal
- Command injection

**Recomendación:**
- Agregar pruebas de seguridad al suite de tests
- Considerar usar herramientas como OWASP ZAP o Burp Suite
- Implementar security scanning en CI/CD

**Prioridad:** Media

---

## 9. Score de Seguridad

| Categoría | Score (0-100) | Justificación |
|-----------|---------------|---------------|
| Protección de datos | 40/100 | RLS implementado pero credenciales hardcodeadas |
| Seguridad | 30/100 | SECRET_KEY expuesto, contraseñas débiles |
| Gestión de credenciales | 20/100 | Secrets hardcodeados, no gestor de secrets |
| Infraestructura | 60/100 | Docker bien configurado, pero puertos expuestos |
| Riesgo legal | 50/100 | GDPR compliance parcial, PII en logs |
| **Score General** | **40/100** | **Riesgo ALTO - Requiere correcciones críticas** |

---

## 10. Hallazgos Prioritarios

### Críticas (Deben corregirse inmediatamente)

1. **SECRET_KEY hardcodeado** - `security.py` línea 7
2. **Credenciales DB hardcodeadas** - `docker-compose.yml` líneas 13, 33, 58-59
3. **Credenciales en worker** - `tasks.py` línea 15

### Altas (Deben corregirse pronto)

4. **Contraseña de app_user débil** - `docker-compose.yml`
5. **No hay refresh tokens** - `security.py`
6. **Faltan pruebas de seguridad** - Suite de tests

### Medias (Deben corregirse)

7. **CORS permisivo** - `main.py`
8. **Logs con PII** - `logger.py`
9. **No hay rate limiting por usuario** - `ratelimit.py`

### Bajas (Mejoras recomendadas)

10. **Puertos expuestos en producción** - `docker-compose.yml`
11. **No hay SSL en conexión DB** - Configuración DB
12. **No hay encriptación en reposo** - Datos en DB

---

## 11. Recomendaciones Generales

### Inmediatas (Antes de producción)

1. Mover todos los secrets a variables de entorno
2. Usar gestor de secrets (AWS Secrets Manager, Vault)
3. Rotar todas las credenciales comprometidas
4. Implementar HTTPS en producción
5. No exponer puertos de DB y Redis públicamente

### Corto Plazo (1-2 semanas)

6. Implementar refresh tokens
7. Agregar pruebas de seguridad al suite de tests
8. Implementar rate limiting por usuario
9. Configurar SSL en conexión DB
10. Mask PII en logs

### Largo Plazo (1-3 meses)

11. Implementar encriptación en reposo (datos sensibles en DB)
12. Implementar políticas de backup y recuperación
13. Implementar security scanning en CI/CD
14. Implementar auditoría de accesos
15. Implementar monitoreo de seguridad

---

## 12. Conclusión

El proyecto tiene **vulnerabilidades de seguridad CRÍTICAS** que deben corregirse antes de cualquier deployment en producción. Las credenciales hardcodeadas y el SECRET_KEY expuesto representan un riesgo inaceptable para la seguridad del sistema y la privacidad de los usuarios.

**Puntos fuertes:**
- RLS implementado correctamente
- Security headers configurados
- ORM protege contra SQL injection
- Pruebas de seguridad implementadas (CORS, RLS, headers)

**Puntos críticos:**
- SECRET_KEY hardcodeado
- Credenciales de DB hardcodeadas
- No hay gestor de secrets
- No hay refresh tokens
- No hay HTTPS configurado

**Recomendación general:** El proyecto **NO ESTÁ LISTO PARA PRODUCCIÓN** en su estado actual. Se deben corregir las vulnerabilidades críticas antes de cualquier deployment público.
