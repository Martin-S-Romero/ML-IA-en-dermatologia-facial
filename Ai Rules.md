# Reglas de Desarrollo Asistido por IA

## Propósito del documento

Este archivo define las **reglas obligatorias** que cualquier agente de IA (Antigravity, Copilot, LLMs u otros asistentes) debe seguir al colaborar en el desarrollo del proyecto.

El objetivo es garantizar:

* Progreso ordenado y verificable
* Código claro y mantenible
* Validación funcional en cada etapa
* Evitar complejidad innecesaria

Estas reglas tienen **prioridad sobre cualquier sugerencia automática del agente**.

---

## Principios fundamentales

1. **Cada avance debe funcionar antes de continuar**
2. **Nada se construye sin poder probarse**
3. **Primero lo simple, luego lo complejo**
4. **Las dependencias mandan el orden de desarrollo**
5. **Código entendible > código sofisticado**
6. **Sin magia negra**

---

## Regla de validación obligatoria

Antes de avanzar a un nuevo componente o funcionalidad, se debe:

* Ejecutar el sistema localmente
* Validar que el componente funciona de forma aislada
* Validar que funciona integrado con los componentes previos
* Confirmar que los logs reflejan correctamente el comportamiento

**Si algo no funciona, se corrige antes de continuar.**

Nunca se asume que "funcionará después".

---

## Regla de pruebas mínimas

Cada módulo debe tener, como mínimo:

* Una prueba manual reproducible
* Evidencia clara de funcionamiento (log, respuesta API, salida en consola)

Las pruebas automáticas son deseables, pero **no obligatorias** para el MVP académico.

---

## Orden obligatorio de desarrollo (de básico a complejo)

El desarrollo debe seguir estrictamente este orden, salvo justificación técnica documentada:

### 1. Infraestructura mínima

* Docker base
* Estructura de carpetas
* Contenedor backend vacío
* Contenedor frontend vacío

Validación: contenedores levantan correctamente

---

### 2. Sistema de logs

* Logger centralizado
* Logs por nivel (info, warning, error)
* Identificación básica de usuario o request

Validación:

* Los logs se generan
* Los logs se almacenan
* Los errores quedan registrados

---

### 3. Base de datos

* Conexión a base de datos SQL
* Esquema mínimo (usuarios, consentimientos)

Validación:

* Conexión exitosa
* Operaciones CRUD básicas
* Logs registran operaciones y errores

---

### 4. Autenticación y seguridad

* Registro de usuarios
* Login
* Emisión y validación de JWT

Validación:

* Login funcional
* Tokens válidos y expiran correctamente
* Accesos inválidos quedan registrados en logs

---

### 5. API Gateway / Backend orquestador

* Endpoints básicos
* Validación de requests
* Control de acceso

Validación:

* Frontend puede comunicarse solo con el gateway
* Servicios internos no son accesibles directamente

---

### 6. Subida y manejo de imágenes

* Endpoint de subida
* Validación de formato
* Almacenamiento **solo de imágenes censuradas**

Validación:

* Imagen válida se procesa
* Imagen inválida se rechaza
* Todo queda registrado en logs

---

### 7. Procesamiento de imagen

* Detección de rostro
* Recorte
* Censura de ojos y labios

Validación:

* La imagen final está censurada
* Nunca se guarda la imagen original

---

### 8. Análisis cutáneo

* Análisis probabilístico
* Clasificaciones generales

Validación:

* Resultados coherentes
* Lenguaje no clínico
* Manejo de errores robusto

---

### 9. Sistema de recomendaciones

* Uso de modelos ONNX / LLM
* Generación de ingredientes recomendados

Validación:

* El sistema responde
* El tiempo de espera es manejado correctamente

---

### 10. UX de espera y estados

* Procesamiento asíncrono
* Estados: processing / completed / failed

Validación:

* El usuario siempre sabe qué está pasando

---

## Regla de dependencias

Ningún módulo puede desarrollarse si depende de otro que:

* No existe
* No funciona
* No está validado

El agente debe **rechazar avanzar** si se viola esta regla.

---

## Regla de decisiones técnicas

Cuando existan múltiples soluciones:

* Elegir la más simple
* Elegir la más explicable
* Elegir la más fácil de mantener

Toda decisión compleja debe poder justificarse **en la tesis**.

---

## Ética y seguridad (obligatorio)

* No generar diagnósticos médicos
* No almacenar datos sensibles sin censura
* No usar lenguaje clínico
* No ocultar limitaciones del sistema

---

## Rol de la IA

La IA actúa como:

* Asistente técnico
* Guía de buenas prácticas
* Revisor de coherencia

La IA **no toma decisiones finales** ni introduce complejidad innecesaria.

---

## Regla final

> Si no se puede probar, no existe.

Todo avance debe ser **funcional, verificable y explicable** antes de continuar.