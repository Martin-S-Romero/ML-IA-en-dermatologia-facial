Puedes estructurarlo como un README “guía operativa” para que cualquier agente/IA haga auditoría técnica y documentación homogénea del proyecto. La clave es que el README no explique solo “qué hacer”, sino también:

* qué revisar,
* cómo medir,
* cómo puntuar,
* qué evidencias guardar,
* y cómo entregar el resultado.

Te dejo una versión bastante sólida y profesional que puedes adaptar.

---

# README — Agente de Auditoría y Documentación Técnica

## Objetivo

Este documento define las reglas, criterios y formato que debe seguir el agente encargado de analizar, documentar y evaluar el proyecto.

El agente debe generar documentación técnica, análisis de arquitectura, evaluación de calidad, cumplimiento regulatorio y estimación económica del desarrollo realizado.

---

# Alcance del análisis

El agente debe analizar:

* Arquitectura del proyecto
* Código fuente
* Estructura de carpetas
* Infraestructura
* Commits y Git history
* Variables sensibles
* Calidad de código
* Pruebas unitarias
* Costos estimados del desarrollo
* Regulaciones aplicables en Panamá

---

# Resultado esperado

El agente debe generar:

1. Documento técnico completo
2. Evaluación de arquitectura
3. Riesgos encontrados
4. Recomendaciones técnicas
5. Estimación económica del proyecto
6. Reporte de cumplimiento regulatorio
7. Score general del proyecto

---

# 1. Análisis de Arquitectura Limpia

## Objetivo

Evaluar si el proyecto sigue principios de:

* Clean Architecture
* SOLID
* Separation of Concerns
* Modularidad
* Escalabilidad
* Mantenibilidad

---

## Revisiones obligatorias

El agente debe revisar:

### Separación de capas

Validar existencia y correcta separación de:

* Domain
* Application
* Infrastructure
* Presentation
* Shared/Common

---

### Dependencias

Detectar:

* Dependencias circulares
* Acoplamiento fuerte
* Clases utilitarias excesivas
* Lógica de negocio en controladores
* Acceso directo a DB desde capas incorrectas

---

### Calidad estructural

Evaluar:

* Modularidad
* Reutilización
* Cohesión
* Complejidad
* Legibilidad
* Escalabilidad

---

## Score requerido

Generar score de 0–100 para:

| Área            | Score |
| --------------- | ----- |
| Arquitectura    |       |
| Modularidad     |       |
| Escalabilidad   |       |
| Mantenibilidad  |       |
| Calidad General |       |

---

## Hallazgos

El agente debe documentar:

* Problemas encontrados
* Impacto técnico
* Riesgo
* Recomendación
* Prioridad (Alta/Media/Baja)

---

# 2. Regulaciones aplicables — Panamá

## Objetivo

Evaluar cumplimiento técnico/legal basado en regulaciones de Panamá.

---

## Revisiones mínimas

El agente debe validar:

### Protección de datos

Considerar:

* Ley 81 de Protección de Datos Personales
* Manejo de PII
* Almacenamiento de datos sensibles
* Consentimiento
* Retención de datos

---

### Seguridad

Validar:

* Variables sensibles expuestas
* Secrets hardcodeados
* Tokens/API keys
* Configuración insegura
* Logs sensibles

---

### Infraestructura

Evaluar:

* Región cloud utilizada
* Riesgos de residencia de datos
* Backups
* Disponibilidad
* Control de acceso

---

## Resultado esperado

Generar:

| Categoría               | Estado |
| ----------------------- | ------ |
| Protección de datos     |        |
| Seguridad               |        |
| Gestión de credenciales |        |
| Infraestructura         |        |
| Riesgo legal            |        |

---

# 3. Estimación de costo del proyecto

## Objetivo

Calcular costo estimado del desarrollo basándose en:

* Tiempo invertido
* Complejidad
* Roles necesarios
* Horas estimadas
* Salario promedio por rol

---

## Roles mínimos a considerar

* Backend Developer
* Frontend Developer
* Cloud Engineer
* DevOps Engineer
* QA Engineer
* Technical Lead
* UI/UX Designer
* Project Manager

---

## Fórmula requerida

Costo por tarea:

```text
Horas estimadas × salario por hora del rol
```

Costo total:

```text
Σ (horas × salario por rol)
```

---

## Consideraciones

El agente debe estimar:

* Nivel de complejidad
* Tiempo de desarrollo
* Tiempo de testing
* Tiempo de arquitectura
* Tiempo de documentación
* Tiempo DevOps/infraestructura

---

## Resultado esperado

Tabla ejemplo:

| Rol     | Horas | Salario/Hora | Subtotal |
| ------- | ----- | ------------ | -------- |
| Backend |       |              |          |
| DevOps  |       |              |          |
| QA      |       |              |          |

---

## Estimación final

Generar:

* Costo mínimo
* Costo promedio
* Costo enterprise
* Tiempo estimado de desarrollo
* Cantidad sugerida de personas

---

# 4. Evaluación General del Proyecto

## Objetivo

Realizar auditoría técnica global.

---

## Revisiones obligatorias

### Testing

Validar:

* Existencia de pruebas unitarias
* Cobertura
* Casos edge
* Mocking
* Integración
* E2E

---

### Seguridad

Detectar:

* Variables expuestas
* Credenciales hardcodeadas
* Secrets en commits
* Configuraciones inseguras

---

### Git y commits

Analizar:

* Calidad de commits
* Frecuencia
* Tamaño de cambios
* Uso de ramas
* Conventional commits
* Commits inseguros
* Commits masivos
* Código sin revisión

---

### Calidad de código

Evaluar:

* Duplicación
* Complejidad ciclomática
* Naming
* Manejo de errores
* Logs
* Validaciones
* Código muerto
* TODOs/FIXMEs

---

## Resultado esperado

Score general:

| Categoría         | Score |
| ----------------- | ----- |
| Seguridad         |       |
| Testing           |       |
| Git Hygiene       |       |
| Calidad de código |       |
| Infraestructura   |       |
| Arquitectura      |       |

---

# Formato de salida requerido

El agente debe generar:

```text
/docs
    architecture-analysis.md
    security-analysis.md
    panama-regulations.md
    cost-estimation.md
    git-review.md
    testing-review.md
    final-report.md
```

---

# Reglas del agente

## El agente DEBE

* Justificar cada hallazgo
* Mostrar evidencia técnica
* Ser crítico y objetivo
* Detectar riesgos reales
* Priorizar problemas
* Explicar impacto técnico y económico

---

## El agente NO DEBE

* Inventar información
* Asumir arquitectura no existente
* Ignorar configuraciones inseguras
* Omitir evidencia
* Generar recomendaciones genéricas

---

# Prioridad de severidad

| Severidad | Definición                       |
| --------- | -------------------------------- |
| Crítica   | Riesgo alto de seguridad o caída |
| Alta      | Problema serio de mantenibilidad |
| Media     | Problema técnico moderado        |
| Baja      | Mejora recomendada               |

---

# Resultado Final Esperado

El agente debe concluir con:

* Estado general del proyecto
* Riesgo técnico
* Riesgo económico
* Riesgo de seguridad
* Nivel de madurez del sistema
* Recomendación final:

  * Aprobado
  * Aprobado con observaciones
  * Requiere refactor
  * Riesgo alto / No recomendado

---

Eso ya está cerca de un estándar de auditoría técnica real. Y honestamente, si lo combinas luego con prompts específicos por sección, puedes convertirlo en un pipeline semi-automatizado bastante potente para revisar repositorios completos.
