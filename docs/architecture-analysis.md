# Análisis de Arquitectura - SkinAI

**Fecha de auditoría:** Mayo 2026  
**Auditor:** Agente de Auditoría Técnica  
**Proyecto:** SkinAI - Plataforma Web de Análisis Cutáneo Asistido por IA

---

## 1. Separación de Capas

### 1.1 Estructura Detectada

El proyecto sigue una arquitectura **monolítica modular** con separación parcial de responsabilidades:

```
backend/app/
├── api/              ← Capa de Presentación (Routers, Endpoints)
├── core/             ← Capa de Dominio (Lógica de negocio, Utilidades)
├── models.py         ← Capa de Persistencia (ORM)
├── schemas.py        ← DTOs/Contratos
└── worker/           ← Procesamiento asíncrono (Celery)
```

**Capas identificadas:**
- **Presentation Layer:** `app/api/` - Routers FastAPI, validación de entrada/salida
- **Domain Layer:** `app/core/` - Lógica de negocio (FaceCensor, Security, Logger)
- **Persistence Layer:** `app/models.py` + `app/core/database.py` - SQLAlchemy ORM
- **Async Processing:** `app/worker/` - Tareas Celery separadas

### 1.2 Evaluación de Separación

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Separación API vs Lógica de negocio | ✅ Parcial | La lógica de negocio está en `core/`, pero hay lógica de negocio mezclada en routers (ej: `products.py` helper `_get_top_per_category`) |
| Separación ORM vs Business Logic | ✅ Bien | Models están separados en `models.py` |
| DTOs separados de Models | ✅ Bien | Schemas Pydantic en `schemas.py` |
| Configuración separada | ⚠️ Parcial | Algunos configs están hardcodeados (SECRET_KEY) |
| Procesamiento asíncrono separado | ✅ Bien | Worker Celery en contenedor separado |

**Hallazgo:** La arquitectura no sigue estrictamente Clean Architecture (no hay Domain, Application, Infrastructure layers separados), pero tiene una separación funcional aceptable para un MVP.

---

## 2. Dependencias

### 2.1 Dependencias Circulares

**Estado:** ✅ No detectadas

No se encontraron dependencias circulares entre los módulos del backend. El flujo de dependencias es unidireccional:
- `api/` → depende de `core/`, `models/`, `schemas/`
- `core/` → depende de `models/`
- `worker/` → depende de `core/`, `models/`

### 2.2 Acoplamiento

| Tipo | Estado | Severidad |
|------|--------|-----------|
| Acoplamiento fuerte entre routers y DB | ⚠️ Detectado | Media |
| Lógica de negocio en routers | ⚠️ Detectado | Media |
| Dependencia directa a SQLAlchemy en routers | ⚠️ Detectado | Media |
| Utilidades excesivas | ❌ No detectado | - |

**Evidencia:**
- `products.py` contiene helper `_get_top_per_category()` con lógica de negocio que debería estar en un servicio separado
- `routines.py` contiene lógica de validación de `analysis_id` directamente en el router

**Recomendación:** Extraer lógica de negocio a una capa de servicios (`app/services/`) para reducir acoplamiento.

---

## 3. Calidad Estructural

### 3.1 Modularidad

| Módulo | Estado | Observación |
|--------|--------|-------------|
| Backend (FastAPI) | ✅ Bien | Modularizado por dominio (auth, users, analysis, routines, products) |
| Frontend (Vite/JS) | ⚠️ Aceptable | Estructura de carpetas organizada, pero sin framework de componentes |
| Worker (Celery) | ✅ Bien | Separado en contenedor propio |
| Scraper | ✅ Bien | Módulo separado en `backend/scraper/` |

### 3.2 Reutilización

| Componente | Reutilizable | Observación |
|-------------|--------------|-------------|
| FaceCensor | ✅ Sí | Clase reutilizable con parámetros configurables |
| Security functions | ✅ Sí | Funciones de hash/JWT reutilizables |
| Logger | ✅ Sí | Logger centralizado reutilizable |
| Routers | ⚠️ Parcial | Algunos endpoints tienen lógica duplicada (validación de user_id) |

### 3.3 Cohesión

| Módulo | Cohesión | Observación |
|--------|----------|-------------|
| `app/api/auth.py` | ✅ Alta | Solo lógica de autenticación |
| `app/api/users.py` | ✅ Alta | Solo lógica de usuarios/perfil |
| `app/api/analysis.py` | ✅ Alta | Solo lógica de análisis |
| `app/core/face_censor.py` | ✅ Alta | Solo lógica de censura facial |
| `app/core/security.py` | ⚠️ Media | Mezcla configuración con implementación |

### 3.4 Escalabilidad

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Escalabilidad horizontal | ⚠️ Limitada | Backend monolítico, pero Docker-ready |
| Escalabilidad vertical | ✅ Buena | Arquitectura stateless (excepto DB) |
| Separación de servicios | ⚠️ Parcial | Worker separado, pero API monolítica |
| Base de datos | ⚠️ Limitada | PostgreSQL single instance, no sharding |

**Recomendación:** Para escalar a producción, considerar migrar a microservicios (API, Worker, Scraper separados) y agregar caché (Redis ya presente).

### 3.5 Mantenibilidad

| Aspecto | Score | Observación |
|---------|-------|-------------|
| Legibilidad del código | 7/10 | Código limpio, pero falta documentación en funciones |
| Consistencia de naming | 8/10 | Naming consistente (snake_case Python, camelCase JS) |
| Manejo de errores | 7/10 | Try/except presentes, pero algunos genéricos |
| Logs | 8/10 | Logger centralizado con formato JSON |
| Validaciones | 8/10 | Pydantic schemas bien definidos |

---

## 4. Score de Arquitectura

| Área | Score (0-100) | Justificación |
|------|---------------|---------------|
| Arquitectura | 65/100 | Monolito modular, no Clean Architecture estricta |
| Modularidad | 75/100 | Buena separación por dominio, pero lógica mezclada |
| Escalabilidad | 60/100 | Docker-ready pero monolítico, limitado para alta carga |
| Mantenibilidad | 75/100 | Código limpio, buena estructura, falta documentación |
| Calidad General | 69/100 | Arquitectura aceptable para MVP, requiere refactor para producción |

---

## 5. Hallazgos y Recomendaciones

### Hallazgo #1: Lógica de Negocio en Routers

**Severidad:** Media  
**Impacto:** Dificulta testing, reutilización y mantenimiento  
**Evidencia:** `products.py` contiene `_get_top_per_category()` con lógica de negocio

**Recomendación:**
```python
# Crear app/services/product_service.py
class ProductService:
    @staticmethod
    def get_recommended_products(user_profile, db):
        # Mover lógica desde products.py aquí
        pass
```

**Prioridad:** Media

---

### Hallazgo #2: Configuración Hardcodeada

**Severidad:** Alta  
**Impacto:** Riesgo de seguridad, dificultad de deployment  
**Evidencia:** `security.py` línea 7: `SECRET_KEY = "tesis-secret-key-change-me-in-production"`

**Recomendación:**
```python
# Usar variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
```

**Prioridad:** Alta (Crítica para producción)

---

### Hallazgo #3: Falta de Capa de Servicios

**Severidad:** Media  
**Impacto:** Acoplamiento, dificulta testing unitario  
**Evidencia:** Routers acceden directamente a DB y contienen lógica de negocio

**Recomendación:** Implementar patrón Service Layer:
```
app/services/
├── auth_service.py
├── user_service.py
├── analysis_service.py
└── product_service.py
```

**Prioridad:** Media

---

### Hallazgo #4: No Hay Inyección de Dependencias

**Severidad:** Baja  
**Impacto:** Dificulta mocking en tests  
**Evidencia:** Dependencias directas (ej: `SessionLocal()` en funciones)

**Recomendación:** Considerar usar dependency injection (FastAPI ya lo usa parcialmente con `Depends()`)

**Prioridad:** Baja

---

## 6. Conclusión

El proyecto tiene una **arquitectura monolítica modular aceptable para un MVP**, con separación funcional clara entre dominios. Sin embargo, no sigue principios de Clean Architecture estrictos, lo que podría limitar su escalabilidad y mantenibilidad a largo plazo.

**Puntos fuertes:**
- Separación clara por dominio funcional
- Procesamiento asíncrono separado (Celery)
- ORM bien estructurado
- DTOs separados de modelos

**Puntos débiles:**
- Lógica de negocio mezclada en routers
- Configuración hardcodeada
- Falta de capa de servicios
- Monolito limita escalabilidad horizontal

**Recomendación general:** Para evolucionar a producción, considerar:
1. Extraer lógica de negocio a capa de servicios
2. Migrar configuración a variables de entorno
3. Evaluar migración a microservicios si se requiere alta escalabilidad
4. Agregar documentación técnica a módulos clave
