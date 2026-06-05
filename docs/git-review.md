# Revisión de Git y Commits - SkinAI

**Fecha de auditoría:** Mayo 2026  
**Auditor:** Agente de Auditoría Técnica  
**Proyecto:** SkinAI - Plataforma Web de Análisis Cutáneo Asistido por IA

---

## 1. Historial de Commits

### 1.1 Resumen del Repositorio

| Métrica | Valor |
|---------|-------|
| Total de commits | 12 |
| Ramas | 5 (main, dev, Phase1, Phase3-4, Phase5-6, Phase7-8) |
| Autores | 2 (Martin-S-Romero, adriana-gesp) |
| Primer commit | 31 enero 2026 |
| Último commit | 27 abril 2026 |
| Duración del proyecto | ~3 meses |

---

## 2. Análisis de Commits

### 2.1 Lista de Commits

| Hash | Mensaje | Fecha | Archivos Cambiados | Autor |
|------|---------|-------|-------------------|-------|
| 36a9379 | feat: Aumento en seguridad y test automaticos | 27 abr 2026 | 13 archivos | adriana-gesp |
| e63157f | docker & emojis update | 27 abr 2026 | 13 archivos | adriana-gesp |
| d5c2af3 | guardando antes de cambiar de rama | 20 abr 2026 | 1 archivo | adrianagonzalez4 |
| 50031fa | Cambios nuevos. Archivos modificados y creados. | 20 abr 2026 | 50 archivos | adrianagonzalez4 |
| 79b3d23 | FT: Procesamiento de foto, guardado y censura | 17 feb 2026 | 6 archivos | Martin-S-Romero |
| 8ae3e76 | FT: upload de imagen | 31 ene 2026 | 6 archivos | Martin-S-Romero |
| 8dba84f | FT: seguridad en el backend | 31 ene 2026 | 4 archivos | Martin-S-Romero |
| 8b3f3f1 | FT: Registro de user y generacion de token | 31 ene 2026 | 10 archivos | Martin-S-Romero |
| 7aefc4c | FT: Creacion del sistema de logs perdurable | 31 ene 2026 | 4 archivos | Martin-S-Romero |
| af849d0 | FT: Esqueleto incial del proyecto | 31 ene 2026 | 5 archivos | Martin-S-Romero |
| ac9995d | first commit | 31 ene 2026 | - | Martin-S-Romero |

---

## 3. Calidad de Commits

### 3.1 Uso de Conventional Commits

| Categoría | Estado | Observación |
|-----------|--------|-------------|
| Formato estándar | ⚠️ Parcial | Algunos commits usan "FT:" prefix, otros no |
| Tipo de commit | ⚠️ Inconsistente | Mezcla de "feat:", "FT:", y mensajes genéricos |
| Scope | ❌ No usado | No hay scope en los commits |
| Descripción | ⚠️ Variable | Algunos descriptivos, otros genéricos |
| Body | ❌ No usado | No hay body en los commits |
| Footer | ❌ No usado | No hay footer (breaking changes, etc.) |

**Ejemplos:**
```
✅ Bueno: feat: Aumento en seguridad y test automaticos
⚠️ Aceptable: FT: Procesamiento de foto, guardado y censura
❌ Malo: guardando antes de cambiar de rama
❌ Malo: Cambios nuevos. Archivos modificados y creados.
```

---

### 3.2 Frecuencia de Commits

| Período | Commits | Frecuencia |
|---------|---------|------------|
| Enero 2026 | 6 | Alta (día de desarrollo intensivo) |
| Febrero 2026 | 1 | Baja |
| Marzo 2026 | 0 | Nula |
| Abril 2026 | 5 | Media |

**Observación:** Hay un gap de 2 meses (marzo) sin commits, lo que sugiere pausa en desarrollo.

---

### 3.3 Tamaño de Cambios

| Commit | Archivos Cambiados | Líneas Añadidas | Líneas Eliminadas | Tamaño |
|--------|-------------------|----------------|-------------------|--------|
| 50031fa | 50 | 7,964 | 97 | Masivo |
| 36a9379 | 13 | 103 | 102 | Mediano |
| e63157f | 13 | 103 | 102 | Mediano |
| 79b3d23 | 6 | 376 | 6 | Grande |
| 8ae3e76 | 6 | 133 | 4 | Mediano |
| 8b3f3f1 | 10 | 226 | 5 | Mediano |
| 7aefc4c | 4 | 219 | 0 | Mediano |
| af849d0 | 5 | 62 | 0 | Pequeño |

**Hallazgo:** El commit 50031fa es **excesivamente grande** (50 archivos, 7,964 líneas añadidas). Esto indica un "big bang commit" que debería haberse dividido.

---

## 4. Uso de Ramas

### 4.1 Estructura de Ramas

| Rama | Estado | Propósito |
|------|--------|----------|
| main | ✅ Activa | Rama principal de producción |
| dev | ✅ Activa | Rama de desarrollo |
| Phase1 | ✅ Mergeada | Fase 1 del proyecto |
| Phase3-4 | ✅ Mergeada | Fases 3-4 del proyecto |
| Phase5-6 | ✅ Mergeada | Fases 5-6 del proyecto |
| Phase7-8 | ✅ Activa | Fases 7-8 del proyecto (actual) |

**Observación:** Se usa un modelo de branching por fases (Phase-based), no Git Flow o GitHub Flow estándar.

---

### 4.2 Estrategia de Branching

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Branching strategy | ⚠️ Custom | Phase-based, no estándar |
| Feature branches | ❌ No usado | Todo en ramas de fase |
| Pull requests | ✅ Usados | Hay evidencia de merge PR #1 |
| Code reviews | ❌ No documentado | No hay evidencia de reviews |
| Branch protection | ❌ No configurado | No hay protección de ramas |

---

## 5. Commits Inseguros

### 5.1 Secrets en Commits

| Archivo | Secret | Hash del Commit | Severidad |
|---------|--------|-----------------|-----------|
| `backend/app/core/security.py` | SECRET_KEY hardcodeado | 8b3f3f1 | Crítica |
| `docker-compose.yml` | DATABASE_URL con contraseña | 8b3f3f1 | Crítica |
| `docker-compose.yml` | POSTGRES_PASSWORD | 8b3f3f1 | Crítica |
| `backend/app/worker/tasks.py` | DATABASE_URL fallback | 50031fa | Crítica |

**Impacto:** Los secrets están expuestos en el historial de Git. Cualquier persona con acceso al repo puede ver las credenciales.

**Recomendación:**
1. Rotar inmediatamente todas las credenciales expuestas
2. Usar `git filter-repo` o BFG Repo-Cleaner para remover secrets del historial
3. Implementar pre-commit hooks para prevenir commits de secrets
4. Usar herramientas como `git-secrets` o `truffleHog`

**Prioridad:** Crítica

---

### 5.2 Datos Sensibles en Commits

| Archivo | Dato Sensible | Hash del Commit | Severidad |
|---------|---------------|-----------------|-----------|
| `image/test_imagen798x1200.jpg` | Imagen de prueba (posiblemente real) | 8ae3e76 | Media |
| `test_imagen530x626.avif` | Imagen de prueba | 8ae3e76 | Media |

**Observación:** Imágenes de prueba están en el repositorio. Si son imágenes reales de usuarios, esto es una violación de privacidad.

**Recomendación:**
1. Verificar si las imágenes son de prueba o reales
2. Si son reales, remover inmediatamente del historial
3. Agregar imágenes a `.gitignore`
4. Usar sistema de almacenamiento externo para datos de prueba

**Prioridad:** Alta

---

## 6. Código Sin Revisión

### 6.1 Evidencia de Code Reviews

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| Pull requests | ✅ Existe | Hay merge de PR #1 |
| Code reviews | ❌ No documentado | No hay evidencia de reviews |
| Approvals | ❌ No configurado | No hay requisitos de aprobación |
| CI checks | ⚠️ Parcial | No hay CI/CD configurado |

**Hallazgo:** Aunque hay evidencia de un PR, no hay documentación de code reviews sistemáticos.

**Recomendación:**
1. Implementar code reviews obligatorios para todos los PRs
2. Configurar branch protection rules
3. Requerir al menos 1 aprobación antes de merge
4. Implementar CI/CD con checks automáticos

**Prioridad:** Alta

---

## 7. Commits Masivos

### 7.1 Commits Problemáticos

| Hash | Problema | Severidad | Recomendación |
|------|----------|-----------|---------------|
| 50031fa | 50 archivos, 7,964 líneas | Alta | Dividir en commits más pequeños |
| d5c2af3 | Mensaje genérico "guardando antes de cambiar de rama" | Media | Usar mensaje descriptivo |
| ac9995d | Mensaje "first commit" genérico | Baja | Usar "chore: initial commit" |

**Recomendación general:**
- Limitar commits a máximo 10-15 archivos
- Escribir mensajes descriptivos que expliquen el "por qué"
- Dividir cambios lógicos en commits separados

---

## 8. Git Hygiene Score

| Categoría | Score (0-100) | Justificación |
|-----------|---------------|---------------|
| Calidad de mensajes | 50/100 | Inconsistente, no conventional commits estrictos |
| Frecuencia de commits | 60/100 | Gap de 2 meses sin actividad |
| Tamaño de commits | 40/100 | Commit masivo de 50 archivos |
| Uso de ramas | 70/100 | Estrategia custom pero funcional |
| Code reviews | 30/100 | No hay evidencia de reviews sistemáticos |
| Seguridad | 20/100 | Secrets hardcodeados en commits |
| **Score General** | **45/100** | **Riesgo ALTO - Requiere mejoras significativas** |

---

## 9. Hallazgos y Recomendaciones

### Hallazgo #1: Secrets Hardcodeados en Commits (CRÍTICO)

**Severidad:** Crítica  
**Evidencia:** SECRET_KEY, DATABASE_URL, POSTGRES_PASSWORD en commits  
**Impacto:** Credenciales expuestas en historial de Git

**Recomendación:**
1. Rotar todas las credenciales inmediatamente
2. Remover secrets del historial con `git filter-repo`
3. Implementar pre-commit hooks
4. Usar `git-secrets` para prevenir futuros commits

**Prioridad:** Crítica

---

### Hallazgo #2: Commit Masivo (ALTA)

**Severidad:** Alta  
**Evidencia:** Commit 50031fa con 50 archivos y 7,964 líneas  
**Impacto:** Dificulta code review, debugging, y rollback

**Recomendación:**
1. Dividir commits grandes en cambios lógicos más pequeños
2. Limitar a máximo 10-15 archivos por commit
3. Usar commits atómicos (un cambio por commit)

**Prioridad:** Alta

---

### Hallazgo #3: No Hay Code Reviews Sistemáticos (ALTA)

**Severidad:** Alta  
**Evidencia:** No hay evidencia de code reviews obligatorios  
**Impacto:** Código no revisado, mayor riesgo de bugs

**Recomendación:**
1. Implementar branch protection rules
2. Requerir al menos 1 aprobación antes de merge
3. Configurar CI/CD con checks automáticos
4. Documentar proceso de code review

**Prioridad:** Alta

---

### Hallazgo #4: Mensajes de Commits Inconsistentes (MEDIA)

**Severidad:** Media  
**Evidencia:** Mezcla de "feat:", "FT:", y mensajes genéricos  
**Impacto:** Dificulta entender el historial de cambios

**Recomendación:**
1. Adoptar Conventional Commits estándar
2. Usar formato: `type(scope): description`
3. Configurar commitlint para validar mensajes
4. Documentar convención de commits

**Prioridad:** Media

---

### Hallazgo #5: Gap de 2 Meses Sin Commits (BAJA)

**Severidad:** Baja  
**Evidencia:** No hay commits en marzo 2026  
**Impacto:** Posible pausa en desarrollo, pero no es un problema técnico

**Recomendación:**
- Documentar razones de la pausa
- Considerar usar milestones para tracking

**Prioridad:** Baja

---

## 10. Recomendaciones Generales

### Inmediatas (Esta semana)

1. **Rotar todas las credenciales expuestas** en el historial de Git
2. **Remover secrets del historial** usando `git filter-repo`
3. **Implementar pre-commit hooks** para prevenir commits de secrets

### Corto Plazo (2-4 semanas)

4. **Configurar branch protection rules** en GitHub/GitLab
5. **Implementar code reviews obligatorios** para todos los PRs
6. **Adoptar Conventional Commits** estándar
7. **Configurar commitlint** para validar mensajes

### Largo Plazo (1-3 meses)

8. **Implementar CI/CD** con checks automáticos
9. **Migrar a Git Flow o GitHub Flow** estándar
10. **Documentar proceso de Git** y convenciones
11. **Implementar automatización** para security scanning en PRs

---

## 11. Herramientas Recomendadas

### Para Prevenir Commits de Secrets

- **git-secrets:** Previene commits de secrets
- **truffleHog:** Escanea historial buscando secrets
- **gitleaks:** Detecta secrets en código

### Para Validar Commits

- **commitlint:** Valida mensajes de commits
- **husky:** Git hooks para Node.js
- **pre-commit:** Git hooks para Python

### Para Code Reviews

- **GitHub Pull Requests:** Code reviews integrados
- **GitLab Merge Requests:** Code reviews integrados
- **SonarQube:** Análisis estático de código

### Para CI/CD

- **GitHub Actions:** CI/CD integrado en GitHub
- **GitLab CI:** CI/CD integrado en GitLab
- **Jenkins:** CI/CD flexible

---

## 12. Conclusión

El historial de Git del proyecto tiene **problemas significativos de seguridad** debido a secrets hardcodeados en commits. Además, la calidad de los commits es inconsistente y no hay evidencia de code reviews sistemáticos.

**Puntos fuertes:**
- Uso de ramas por fases (aunque no estándar)
- Evidencia de pull requests
- Commits descriptivos en su mayoría

**Puntos críticos:**
- Secrets hardcodeados en commits (CRÍTICO)
- Commit masivo de 50 archivos
- No hay code reviews sistemáticos
- Mensajes de commits inconsistentes

**Recomendación general:** El proyecto requiere **mejoras urgentes en Git hygiene**, especialmente en seguridad (remover secrets del historial) y proceso de code reviews. Se deben implementar las recomendaciones críticas inmediatamente.
