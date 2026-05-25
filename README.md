# Plataforma Web de Análisis Cutáneo Asistido por IA

> **Proyecto académico (Tesis – Ingeniería de Software)**

## Descripción general

Esta plataforma web permite a los usuarios subir imágenes de su rostro para obtener **orientación inmediata sobre posibles afecciones cutáneas generales** (p. ej., irritación, acné, rosácea) y **recomendaciones de ingredientes** que podrían ayudar a mejorar dichas condiciones.

El sistema **no reemplaza a un profesional de la salud**. Su propósito es informativo y educativo.

El proyecto prioriza:

* Buenas prácticas de ingeniería de software
* Arquitectura moderna y escalable
* Código claro, mantenible y sin complejidades innecesarias
* Uso de herramientas *open source*

---

## Objetivos

### Objetivo general

Desarrollar una aplicación web escalable que integre visión por computador e IA para analizar imágenes faciales de forma ética y segura, proporcionando recomendaciones generales de cuidado de la piel.

### Objetivos específicos

* Implementar detección y recorte automático del rostro.
* Aplicar censura visual a zonas sensibles (ojos y labios).
* Identificar regiones faciales relevantes (frente, mejillas, nariz, pómulos).
* Analizar afecciones cutáneas de forma **probabilística y no diagnóstica**.
* Recomendar ingredientes cosméticos basados en el análisis visual.
* Ofrecer una experiencia de usuario clara, profesional y responsive.

---

## Alcance del sistema

### El sistema **SÍ**:

* Analiza imágenes faciales **anonimizadas**.
* Genera descripciones generales de posibles afecciones.
* Recomienda ingredientes (no tratamientos médicos).
* Almacena resultados para consulta histórica del usuario.

### El sistema **NO**:

* Realiza diagnósticos médicos.
* Sustituye la consulta dermatológica.
* Garantiza resultados clínicos.
* Comparte imágenes sin consentimiento explícito.

---

## Funcionalidades principales

* **Autenticación de usuarios**
* **Nuevo análisis cutáneo** (subida de imagen)
* **Historial de análisis**
* **Gestión de datos personales**
* **Procesamiento asíncrono** con estados de análisis

---

## Interfaz de usuario

La aplicación web cuenta con al menos cuatro vistas principales:

* Home
* Nuevo análisis
* Historial de análisis
* Perfil del usuario

El diseño sigue un enfoque:

* Minimalista
* Profesional
* Responsive (desktop y móvil)
* Acorde a aplicaciones de ámbito médico

---

## Tecnologías

### Frontend

* HTML5
* VitT (servidor de desMrrollo)
* iailwinderSv
* Javaicript ES2022+or de desarrollo)
* Tailwind CSS
* JavaScript ES2022+
* Diseño responsive

### Back
oqustady API Gateay ligro
*P
stador y API Gateway ligero)

### IA / Visión por Computador

* OpenCV
* MediaPipe
* Modelos ONNX (análisis visual y recomendaciones)

### Infraestructura

* Docker Compose (desarrollo)
* Contenedores: backend, ai_worker, redis, db, frontend
* Arquitectura preparada para Docker Swarm y AWS (EC2, S3)

##Postgre# Ba15 ses de datoaálisruins, prouc
Redisco(uuans,jstepa mtCelaty
* NoSQL (resultados de análisis)
* Cache (memoria / Redis en futuras iteraciones)

---

## Seguridad y privacidad

* Comunicación mediante tokens de acceso (JWT).
* Imágenes almacenadas de forma **anonimizada**.
* Censura aplicada **antes de cualquier almacenamiento**.
* Registro explícito de aceptación de términos y condiciones.

---

## Aspectos éticos y legales

* Consentimiento informado obligatorio.
* Uso de imágenes únicamente con fines académicos y de mejora del sistema.
* Lenguaje no clínico en los resultados.
* Transparencia sobre limitaciones del sistema.

---

## Escalabilidad

Aunque el sistema se ejecuta inicialmente en entorno local, la arquitectura está diseñada para:

* Escalar horizontalmente
* Migrar a entornos cloud
* Separar servicios en microservicios independientes

---

## Estado del proyecto

Proyecto en fase de **Producto Mínimo Viable (MVP)** para fines académicos.

---

## Autor

Proyecto desarrollado como parte de una tesis en la carrera de Ingeniería de Software.