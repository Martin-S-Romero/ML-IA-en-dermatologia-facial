# Arquitectura del Sistema

## 🧱 Visión general

El sistema adopta una **arquitectura modular basada en contenedores**, inspirada en microservicios, pero optimizada para un entorno académico y un MVP mantenible.

La separación es principalmente **lógica**, con la capacidad de evolucionar hacia microservicios independientes conforme el sistema madure.

---

## 🗺️ Diagrama conceptual (alto nivel)

```
[ Usuario ]
     |
     v
[ Frontend (React) ]
     |
     v
[ API Gateway / Backend Orquestador ]
     |
     +--> Servicio de Procesamiento de Imagen
     |
     +--> Servicio de Análisis Cutáneo
     |
     +--> Servicio de Recomendaciones
     |
     +--> Base de Datos
     |
     +--> Sistema de Logs
```

---

## 🧩 Componentes principales

### 1. Frontend

* Aplicación web desarrollada en React
* Único punto de entrada del usuario
* Comunicación exclusiva con el API Gateway
* Manejo de estados de análisis (processing, completed, failed)
* Cache en navegador para mejorar UX

---

### 2. API Gateway / Backend Orquestador

Responsabilidades:

* Autenticación y autorización (JWT)
* Validación de solicitudes
* Orquestación del flujo de análisis
* Comunicación con servicios internos
* Control de acceso y aislamiento del sistema

Tecnología sugerida:

* FastAPI (Python)

---

### 3. Servicio de Procesamiento de Imagen

Funciones:

* Detección de rostro (OpenCV + MediaPipe)
* Recorte de imagen
* Censura automática de ojos y labios
* Preparación de regiones faciales de interés

Notas:

* La censura se aplica **antes de cualquier almacenamiento**
* Nunca se persisten imágenes originales sin censura

---

### 4. Servicio de Análisis Cutáneo

Funciones:

* Análisis visual de regiones no censuradas
* Detección probabilística de afecciones generales

  * Irritación
  * Acné
  * Rosácea
  * Otras afecciones leves

Características:

* No diagnóstica
* Resultados expresados como probabilidades o descripciones generales

---

### 5. Servicio de Recomendaciones

Funciones:

* Uso de modelos ONNX y/o LLMs visuales
* Generación de recomendaciones de ingredientes cosméticos
* Lenguaje no clínico

Ejemplo de salida:

> "Ingredientes que podrían ser beneficiosos según el análisis visual"

---

### 6. Almacenamiento

#### Base de datos SQL

* Usuarios
* Consentimientos
* Metadatos de análisis

#### Base de datos NoSQL

* Resultados de análisis
* Información semiestructurada generada por IA

#### Almacenamiento de archivos

* Imágenes censuradas
* Asociadas de forma anónima

---

### 7. Sistema de Logs

Funciones:

* Registro de acciones del usuario
* Trazabilidad de errores
* Monitoreo del sistema

Preparado para:

* Centralización
* Observabilidad en entornos cloud

---

## 🔄 Flujo de procesamiento

1. Usuario sube imagen
2. API Gateway valida y crea un job
3. Procesamiento de imagen y censura
4. Análisis cutáneo
5. Generación de recomendaciones
6. Persistencia de resultados
7. Notificación de estado al frontend

---

## ⏳ Procesamiento asíncrono

Debido a posibles tiempos de espera elevados:

* El análisis se ejecuta como tarea asíncrona
* El usuario visualiza el progreso
* El historial refleja el estado del análisis

---

## 🔐 Seguridad

* JWT con tiempo de expiración
* Aislamiento de servicios internos
* API Gateway como único punto de entrada
* Preparado para rate limiting

---

## 📦 Contenerización

Cada componente puede ejecutarse como contenedor Docker:

* frontend
* backend (gateway/orquestador)
* servicios de análisis
* base de datos
* logs

La arquitectura está preparada para:

* Docker Swarm
* Despliegue en AWS (EC2, S3)

---

## 📐 Principios arquitectónicos

* Simplicidad sobre complejidad
* Código claro y explícito
* Separación de responsabilidades
* Escalabilidad progresiva
* Sin dependencias innecesarias

---

## 🧠 Filosofía del sistema

> Escalable, ético y mantenible.

El sistema prioriza decisiones de ingeniería comprensibles, evitando "magia negra" y favoreciendo soluciones que puedan ser explicadas, defendidas y mantenidas a largo plazo.