# Estimación de Costo del Proyecto - SkinAI

**Fecha de estimación:** Mayo 2026  
**Estimador:** Agente de Auditoría Técnica  
**Proyecto:** SkinAI - Plataforma Web de Análisis Cutáneo Asistido por IA

---

## 1. Metodología de Estimación

### 1.1 Fórmula Utilizada

**Costo por tarea:**
```
Horas estimadas × salario por hora del rol
```

**Costo total:**
```
Σ (horas × salario por rol)
```

### 1.2 Salarios por Hora (Panamá - 2026)

| Rol | Salario/Hora (USD) | Fuente |
|-----|-------------------|--------|
| Backend Developer (Senior) | $45 | Mercado local |
| Frontend Developer (Senior) | $40 | Mercado local |
| Cloud Engineer (Senior) | $50 | Mercado local |
| DevOps Engineer (Senior) | $48 | Mercado local |
| QA Engineer (Mid) | $35 | Mercado local |
| Technical Lead (Senior) | $60 | Mercado local |
| UI/UX Designer (Mid) | $38 | Mercado local |
| Project Manager (Mid) | $42 | Mercado local |

---

## 2. Desglose por Rol

### 2.1 Backend Developer

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Arquitectura inicial | 40 | $1,800 |
| Desarrollo API (auth, users) | 60 | $2,700 |
| Desarrollo API (analysis, routines) | 80 | $3,600 |
| Integración IA (FaceCensor) | 60 | $2,700 |
| Implementación Celery + Redis | 40 | $1,800 |
| Scraping de productos | 50 | $2,250 |
| Testing unitario | 30 | $1,350 |
| Debugging y fixes | 40 | $1,800 |
| Documentación técnica | 20 | $900 |
| **Total Backend** | **420** | **$18,900** |

---

### 2.2 Frontend Developer

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Diseño UI/UX (colaboración) | 30 | $1,200 |
| Setup Vite + Tailwind | 20 | $800 |
| Desarrollo SPA (router) | 40 | $1,600 |
| Páginas (landing, auth, profile) | 50 | $2,000 |
| Página de captura de foto | 30 | $1,200 |
| Dashboard (tabs, gráficas) | 60 | $2,400 |
| Integración API | 50 | $2,000 |
| Responsive design | 30 | $1,200 |
| Testing manual | 20 | $800 |
| Debugging y fixes | 30 | $1,200 |
| **Total Frontend** | **360** | **$14,400** |

---

### 2.3 Cloud/DevOps Engineer

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Diseño arquitectura cloud | 30 | $1,500 |
| Configuración Docker | 25 | $1,250 |
| Docker Compose orquestación | 20 | $1,000 |
| Configuración PostgreSQL | 15 | $750 |
| Configuración Redis | 10 | $500 |
| Setup CI/CD (GitHub Actions) | 30 | $1,500 |
| Configuración seguridad (SSL, secrets) | 25 | $1,250 |
| Monitoring y logging | 20 | $1,000 |
| Backup strategy | 15 | $750 |
| Documentación infraestructura | 10 | $500 |
| **Total Cloud/DevOps** | **180** | **$9,000** |

---

### 2.4 QA Engineer

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Plan de pruebas | 20 | $700 |
| Pruebas unitarias (backend) | 40 | $1,400 |
| Pruebas de integración | 30 | $1,050 |
| Pruebas E2E | 40 | $1,400 |
| Pruebas de seguridad | 25 | $875 |
| Pruebas de performance | 20 | $700 |
| Pruebas de compatibilidad | 15 | $525 |
| Reporte de bugs | 20 | $700 |
| **Total QA** | **190** | **$6,650** |

---

### 2.5 Technical Lead

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Arquitectura técnica | 40 | $2,400 |
| Code reviews | 60 | $3,600 |
| Mentorship equipo | 40 | $2,400 |
| Decisiones técnicas | 20 | $1,200 |
| Gestión de riesgos técnicos | 20 | $1,200 |
| Documentación arquitectónica | 15 | $900 |
| **Total Tech Lead** | **195** | **$11,700** |

---

### 2.6 UI/UX Designer

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Research y benchmarking | 30 | $1,140 |
| Wireframes | 40 | $1,520 |
| Design system (colores, tipografía) | 25 | $950 |
| Mockups de todas las páginas | 50 | $1,900 |
| Prototipos interactivos | 30 | $1,140 |
| Iteraciones basadas en feedback | 25 | $950 |
| Assets y recursos | 15 | $570 |
| **Total UI/UX** | **215** | **$8,170** |

---

### 2.7 Project Manager

| Tarea | Horas Estimadas | Subtotal (USD) |
|-------|-----------------|----------------|
| Planificación del proyecto | 30 | $1,260 |
| Gestión de timeline | 60 | $2,520 |
| Coordinación equipo | 80 | $3,360 |
| Stakeholder management | 30 | $1,260 |
| Reportes de progreso | 25 | $1,050 |
| Gestión de riesgos | 20 | $840 |
| Documentación de proyecto | 15 | $630 |
| **Total PM** | **260** | **$10,920** |

---

## 3. Resumen de Costos

### 3.1 Costo por Rol

| Rol | Horas | Salario/Hora | Subtotal (USD) |
|-----|-------|--------------|----------------|
| Backend Developer | 420 | $45 | $18,900 |
| Frontend Developer | 360 | $40 | $14,400 |
| Cloud/DevOps Engineer | 180 | $48 | $9,000 |
| QA Engineer | 190 | $35 | $6,650 |
| Technical Lead | 195 | $60 | $11,700 |
| UI/UX Designer | 215 | $38 | $8,170 |
| Project Manager | 260 | $42 | $10,920 |
| **TOTAL** | **1,820** | - | **$79,740** |

---

### 3.2 Costo por Fase

| Fase | Horas | Costo (USD) | Porcentaje |
|------|-------|-------------|------------|
| Diseño y Arquitectura | 285 | $13,070 | 16.4% |
| Desarrollo Backend | 420 | $18,900 | 23.7% |
| Desarrollo Frontend | 360 | $14,400 | 18.1% |
| Infraestructura y DevOps | 180 | $9,000 | 11.3% |
| Testing y QA | 190 | $6,650 | 8.3% |
| Gestión y Coordinación | 260 | $10,920 | 13.7% |
| UI/UX Design | 215 | $8,170 | 10.2% |
| **TOTAL** | **1,820** | **$79,740** | **100%** |

---

## 4. Estimación por Complejidad

### 4.1 Complejidad del Proyecto

El proyecto SkinAI tiene una complejidad **MEDIA-ALTA** debido a:

- Integración de IA (MediaPipe, OpenCV)
- Procesamiento asíncrono (Celery + Redis)
- Múltiples tecnologías (Python, JavaScript, Docker)
- Requisitos de seguridad (JWT, RLS, GDPR)
- Scraping de datos externos
- Responsive design

### 4.2 Ajuste por Complejidad

| Factor | Multiplicador | Justificación |
|--------|---------------|---------------|
| Complejidad técnica | 1.2 | IA + procesamiento asíncrono |
| Requisitos de seguridad | 1.1 | JWT, RLS, GDPR compliance |
| Integración de múltiples servicios | 1.1 | Docker, PostgreSQL, Redis, Celery |
| **Multiplicador Total** | **1.43** | - |

---

## 5. Estimación Final

### 5.1 Costo Ajustado

```
Costo base: $79,740
Multiplicador: 1.43
Costo ajustado: $79,740 × 1.43 = $114,028
```

### 5.2 Escenarios de Costo

| Escenario | Multiplicador | Costo Final (USD) | Tiempo Estimado | Equipo Sugerido |
|----------|---------------|------------------|-----------------|-----------------|
| **Mínimo (MVP rápido)** | 1.0 | $79,740 | 3-4 meses | 4 personas |
| **Promedio (realista)** | 1.43 | $114,028 | 4-6 meses | 5-6 personas |
| **Enterprise (robusto)** | 1.8 | $143,532 | 6-9 meses | 7-8 personas |

---

## 6. Desglose por Escenario

### 6.1 Escenario Mínimo (MVP Rápido)

**Equipo:** 4 personas
- Backend Developer (Senior)
- Frontend Developer (Senior)
- Cloud/DevOps Engineer (part-time)
- Project Manager (part-time)

**Horas reducidas:** 1,200 horas (reducción del 34%)
**Costo:** $79,740

**Características:**
- MVP funcional básico
- Testing mínimo
- Sin pruebas de seguridad exhaustivas
- Documentación básica
- Deployment manual

**Riesgos:**
- Calidad inferior
- Deuda técnica acumulada
- Mantenibilidad reducida

---

### 6.2 Escenario Promedio (Realista)

**Equipo:** 5-6 personas
- Backend Developer (Senior)
- Frontend Developer (Senior)
- Cloud/DevOps Engineer (Senior)
- QA Engineer (Mid)
- Technical Lead (part-time)
- Project Manager (part-time)
- UI/UX Designer (part-time)

**Horas:** 1,820 horas
**Costo:** $114,028

**Características:**
- MVP completo con todas las características
- Testing adecuado
- Pruebas de seguridad implementadas
- Documentación técnica completa
- CI/CD automatizado
- Monitoring básico

**Riesgos:**
- Costo más alto
- Tiempo más largo
- Requiere coordinación de equipo

---

### 6.3 Escenario Enterprise (Robusto)

**Equipo:** 7-8 personas
- Backend Developer (Senior) × 2
- Frontend Developer (Senior)
- Cloud/DevOps Engineer (Senior)
- QA Engineer (Senior)
- Technical Lead (Full-time)
- Project Manager (Full-time)
- UI/UX Designer (Full-time)
- Security Engineer (Consultor)

**Horas:** 2,500 horas
**Costo:** $143,532

**Características:**
- Sistema enterprise-ready
- Testing exhaustivo (automatizado + manual)
- Seguridad avanzada (penetration testing)
- Documentación completa (técnica + usuario)
- CI/CD avanzado con múltiples ambientes
- Monitoring y alertas avanzadas
- Soporte 24/7
- SLA definidos

**Riesgos:**
- Costo significativamente más alto
- Tiempo más largo
- Overhead de coordinación

---

## 7. Costos Adicionales

### 7.1 Infraestructura (Mensual)

| Servicio | Costo Mensual (USD) | Costo Anual (USD) |
|----------|---------------------|------------------|
| AWS EC2 (t3.medium × 2) | $60 | $720 |
| AWS RDS PostgreSQL | $50 | $600 |
| AWS ElastiCache Redis | $40 | $480 |
| AWS S3 (storage) | $20 | $240 |
| AWS CloudFront (CDN) | $30 | $360 |
| Domain SSL | $15 | $180 |
| Monitoring (Datadog/New Relic) | $50 | $600 |
| **Total Infraestructura** | **$265** | **$3,180** |

---

### 7.2 Herramientas y Licencias (Anual)

| Herramienta | Costo Anual (USD) |
|-------------|-------------------|
| IDE Licenses (JetBrains) | $200 |
| Design Tools (Figma) | $0 (gratis) |
| Project Management (Jira/Linear) | $300 |
| Communication (Slack) | $0 (gratis) |
| CI/CD (GitHub Actions) | $0 (gratis para uso moderado) |
| **Total Herramientas** | **$500** |

---

### 7.3 Costo Total del Proyecto (Primer Año)

| Categoría | Costo (USD) |
|-----------|-------------|
| Desarrollo (escenario promedio) | $114,028 |
| Infraestructura (primer año) | $3,180 |
| Herramientas (primer año) | $500 |
| Contingencia (15%) | $17,104 |
| **TOTAL PRIMER AÑO** | **$134,812** |

---

## 8. Comparación con Mercado

### 8.1 Costo Promedio en Panamá

| Tipo de Proyecto | Rango de Costo (USD) | SkinAI |
|-----------------|---------------------|--------|
| MVP simple | $50,000 - $80,000 | $79,740 (mínimo) |
| Aplicación web media | $80,000 - $150,000 | $114,028 (promedio) |
| Aplicación enterprise | $150,000 - $300,000 | $143,532 (enterprise) |

**Conclusión:** La estimación de SkinAI está **alineada con el mercado** para proyectos de similar complejidad en Panamá.

---

## 9. Análisis de ROI

### 9.1 Supuestos

- Costo de desarrollo: $114,028 (escenario promedio)
- Costo anual de infraestructura: $3,180
- Costo anual de mantenimiento: $20,000 (20% de desarrollo)
- Precio de suscripción mensual: $15
- Tasa de conversión: 5%
- Costo de adquisición de usuario: $10

### 9.2 Proyección de Ingresos

| Año | Usuarios | Ingresos Anuales (USD) | Costos Anuales (USD) | Profit/Loss |
|-----|---------|----------------------|---------------------|-------------|
| Año 1 | 500 | $90,000 | $137,208 | -$47,208 |
| Año 2 | 2,000 | $360,000 | $23,180 | $336,820 |
| Año 3 | 5,000 | $900,000 | $23,180 | $876,820 |

**Break-even:** Año 2 (aproximadamente 18 meses)

---

## 10. Recomendaciones

### 10.1 Para MVP Inicial

1. **Iniciar con escenario mínimo ($79,740)**
   - Reducir alcance inicial
   - Foco en funcionalidad core
   - Testing manual inicial

2. **Equipo mínimo de 4 personas**
   - 1 Backend Developer
   - 1 Frontend Developer
   - 1 Cloud/DevOps (part-time)
   - 1 PM (part-time)

3. **Timeline: 3-4 meses**
   - Sprint 1: Arquitectura + auth
   - Sprint 2: API core + frontend básico
   - Sprint 3: IA + análisis
   - Sprint 4: Testing + deployment

### 10.2 Para Escalado a Producción

1. **Migrar a escenario promedio ($114,028)**
   - Agregar QA Engineer
   - Agregar Technical Lead
   - Mejorar testing y seguridad

2. **Equipo de 5-6 personas**
   - Timeline extendido a 4-6 meses
   - Mejor calidad y mantenibilidad

3. **Infraestructura robusta**
   - AWS o Azure
   - CI/CD automatizado
   - Monitoring y alertas

---

## 11. Conclusión

El costo estimado para desarrollar SkinAI varía entre **$79,740 (MVP mínimo)** y **$143,532 (enterprise)**, con un escenario promedio de **$114,028**.

**Puntos clave:**
- El costo está alineado con el mercado panameño
- El ROI es positivo a partir del año 2
- El escenario mínimo es viable para un MVP inicial
- El escenario promedio es recomendado para producción
- Los costos de infraestructura son manejables ($265/mes)

**Recomendación final:** Iniciar con el escenario mínimo ($79,740) para validar el producto, luego escalar al escenario promedio ($114,028) para producción robusta.
