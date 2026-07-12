# Guía para la redacción de la tesis — SkinAI (Detección de afecciones cutáneas faciales con Deep Learning)

> Basada en el análisis de dos documentos: (1) tu **Anteproyecto** ya aprobado ("Diseño y Desarrollo de una aplicación basada en Deep Learning para la detección preliminar de afecciones cutáneas en el rostro") y (2) una **tesis terminada de referencia** de Ingeniería de Software de la UTP ("Framework para el análisis del mercado bursátil de acciones"), usada aquí únicamente como modelo de estructura, nivel de detalle y estilo — no de contenido.

---

## 0. Idea general antes de empezar

La tesis de referencia (mercado bursátil) y tu anteproyecto comparten el mismo esqueleto institucional (UTP, Ingeniería de Software), solo que la tesis de referencia colapsa "planteamiento del problema" y "marco teórico" en un solo Capítulo 1, mientras que tu anteproyecto los separa en Capítulo 1 y Capítulo 2. **Usa el plan de contenido de tu anteproyecto como esqueleto oficial** (ya está registrado/aprobado); usa la tesis de referencia como ejemplo de *cómo llenar* cada capítulo: cuánto detalle dar, qué tipo de figuras insertar, cómo documentar decisiones fallidas, cómo comparar arquitecturas, cómo presentar resultados y cómo cerrar con hallazgos.

Tabla de equivalencia entre ambos documentos:

| Tu anteproyecto (plan de contenido) | Tesis de referencia (equivalente) |
|---|---|
| Cap. 1: Planteamiento del problema | Cap. 1: Antecedentes del proyecto (secciones 1.1–1.3) |
| Cap. 2: Marco Teórico | Cap. 1: Antecedentes del proyecto (secciones 1.4–1.5, Marco teórico y Métodos/conceptos) |
| Cap. 3: Metodología de Trabajo | Cap. 2: Marco metodológico + Cap. 3: Arquitectura física y requerimientos |
| Cap. 4: Desarrollo del Proyecto | Cap. 4: Desarrollo del proyecto (la más extensa en ambos casos) |
| Cap. 5: Pruebas y Validación | Cap. 4 (secciones finales: resultados, simulaciones) |
| — (no tenías capítulo dedicado) | Cap. 5: Futuras mejoras — **agrégalo como Capítulo 6** si tu programa lo permite, o como sección final de Cap. 5 |

---

## 1. Páginas preliminares (se escriben AL FINAL, pero se listan aquí porque van primero en el documento)

En este orden exacto (según el ejemplo):

1. Portada institucional (título, asesor, coasesores si aplica, integrantes con cédula, año)
2. Segunda portada con "Trabajo de graduación para optar por el título de..."
3. **Resumen** (1 página): qué se hizo, con qué tecnologías, qué se buscó demostrar/lograr, y la conclusión general. Escríbelo al final, cuando ya sepas los resultados reales.
4. **Dedicatoria**
5. **Agradecimientos**
6. **Índice general** (con numeración de página)
7. **Índice de figuras** (título exacto y número de cada ilustración)
8. **Índice de tablas**
9. **Introducción** (medio página a una página por capítulo, resumiendo qué va a leer el lector en cada uno — es un "mapa" del documento, no el planteamiento del problema)

> Regla práctica del ejemplo: la Introducción del documento completo (la de la página xiii) es distinta de la introducción/antecedentes del Capítulo 1. La primera es un resumen de "qué contiene cada capítulo"; la segunda es el desarrollo real del contexto del proyecto.

---

## 2. Capítulo 1: Planteamiento del problema

Mapea directamente con tu anteproyecto. Amplíalo con lo que ya aprendiste durante el desarrollo (el anteproyecto es una promesa; el Capítulo 1 final es la versión madura, con datos reales).

### 1.1 Problemática
- **1.1.1 Situación actual**: contexto de salud dermatológica, brecha de acceso a dermatólogos (Panamá/región), costos de consulta (puedes retomar tus referencias [9], [12], [14] del anteproyecto sobre precios de clínicas dermatológicas en Panamá).
- **1.1.2 Problema principal**: la falta de una herramienta accesible, gratuita/económica y basada en evidencia que dé una orientación preliminar sobre afecciones cutáneas faciales.
- **1.1.3 Problemas específicos**: por ejemplo, (a) desinformación en redes sociales sobre skincare (tu referencia [17] de TikTok), (b) ausencia de herramientas open-source enfocadas específicamente en rostro, (c) falta de anonimización/censura de datos sensibles en soluciones existentes.

> Nota de estilo tomada del ejemplo: en la tesis de referencia, cada "caso de estudio" (NVDA, QQQ, GLD) se redactó como una subsección independiente con su propia justificación numérica. Tú puedes aplicar la misma lógica describiendo **casos de uso o perfiles de usuario** (ej.: usuario con acné leve, usuario con rosácea, usuario sin afecciones) si decides ilustrar el problema con casos concretos.

### 1.2 Propuesta
- **1.2.1 Justificación**: por qué Deep Learning (CNN / transfer learning) es adecuado para clasificación de imágenes dermatológicas — cita a Esteva et al. 2017 (ya está en tus referencias [5], el paper de Nature sobre clasificación de cáncer de piel con redes neuronales) y Jeong et al. 2022 [6].
- **1.2.2 Delimitación**: solo rostro, no cuerpo completo; carácter informativo/no diagnóstico (esto ya lo tienes muy claro en tu README — cópialo/formalízalo aquí).

### 1.3 Objetivos
Ya los tienes redactados en el anteproyecto. En la tesis final, verifica que:
- El objetivo general sea una sola oración medible.
- Cada objetivo específico se pueda "marcar como cumplido" con una sección del Capítulo 4 (haz una tabla mental: objetivo → dónde se demuestra que se cumplió).

### 1.4 Alcance del proyecto
Usa tu sección "Alcance del sistema" del README (el sistema SÍ hace X, NO hace Y) — es exactamente el tipo de contenido que va aquí.

### 1.5 Impacto social
Redáctalo en la línea de "democratización del acceso a orientación dermatológica", similar al enfoque de FinTech de la tesis de referencia ("brindar herramientas a quienes no son expertos"). Aquí puedes citar el enfoque de Topol [15] (*Deep Medicine*) sobre IA humanizando la salud, y mencionar explícitamente el principio de que **no reemplaza al profesional** (recomendación ética recurrente).

---

## 3. Capítulo 2: Marco Teórico

Aquí es donde más se nota la diferencia con la tesis de referencia (esa es de finanzas/LSTM; la tuya es de visión por computador/dermatología), pero la **estructura** de cómo presentar el marco teórico es igualmente válida:

### 2.1 Antecedentes y tendencias actuales
Sigue el patrón del ejemplo (sección 1.4 "Marco teórico" de la tesis de referencia): resume 4-6 papers/artículos clave, uno por párrafo, indicando: autor, qué hicieron, qué técnica usaron, qué resultado obtuvieron. Ya tienes buen material en tus referencias:
- Esteva et al. (2017) — clasificación de cáncer de piel con redes neuronales profundas, comparado a nivel dermatólogo.
- Jeong et al. (2022) — revisión sistemática de Deep Learning en dermatología (enfoques, resultados, limitaciones).
- Aboulmira et al. (2024) — app SkinHealthMate, plataforma de IA para diagnóstico de piel (antecedente directo/competidor).
- Kleinman (2021, BBC) — herramienta de Google para identificar condiciones de piel.
- Winn (2022, MIT News) — Piction Health, app de clasificación de piel con foto.

### 2.2 Bases teóricas
Aquí defines, con nivel de "libro de texto", los conceptos técnicos que usarás en el Capítulo 4. Con base en el estilo del ejemplo (que dedicó una sección extensa a explicar LSTM, GRU, ARO, GA con nivel de detalle matemático/conceptual), tú deberías explicar aquí, como mínimo:
- **Redes Neuronales Convolucionales (CNN)**: qué son, por qué son el estándar para clasificación/detección en imágenes, capas convolucionales, pooling, feature maps.
- **Transfer Learning / Fine-tuning**: por qué se usa sobre entrenar desde cero (dataset pequeño típico en dermatología), y qué modelos base son candidatos (ResNet, EfficientNet, MobileNet, VGG) — con una tabla comparativa (ver sección de tablas más abajo).
- **Detección y recorte facial** (face detection/landmarks — ej. MediaPipe, dlib, MTCNN): cómo se identifica el rostro y las regiones (frente, mejillas, nariz).
- **Segmentación de regiones faciales**: técnica usada para dividir el rostro en zonas de análisis.
- **Métricas de evaluación de clasificación**: accuracy, precision, recall, F1-score, AUC-ROC, matriz de confusión — con sus fórmulas (igual que el ejemplo puso la fórmula del cambio fraccional, tú debes poner las fórmulas de estas métricas).
- **Ética y anonimización de datos biométricos** (GDPR, censura de ojos/labios) — esto es un diferenciador único de tu proyecto y vale la pena teorizarlo bien, citando normativa de protección de datos.

### 2.3 Definición de términos
Glosario corto (media página) de términos técnicos: dataset, epoch, batch size, overfitting, augmentation, embedding, etc. El ejemplo no tiene esta sección como tal, pero al ser parte de tu plan de contenido aprobado, mantenla — es estándar en tesis de ingeniería.

---

## 4. Capítulo 3: Metodología de Trabajo

### 3.1 Concepción del proyecto
- **3.1.1 Metodología de trabajo**: declara qué metodología de ingeniería de software usaste (Scrum, Kanban, incremental, etc.) — el ejemplo usó "programación orientada a objetos siguiendo PEP8" como su enfoque técnico, pero tú debes declarar tu metodología de **gestión de proyecto** (con sprints o hitos) y tu enfoque técnico (ej. MLOps ligero: dataset → entrenamiento → validación → despliegue).
- **3.1.2 Análisis del proyecto a desarrollar**: aquí es donde va tu **diagrama de casos de uso UML** (no está en el ejemplo porque es un proyecto de análisis de datos, pero es obligatorio en un proyecto con interfaz de usuario como el tuyo). Casos de uso mínimos: registrar/iniciar sesión, subir imagen, ver resultado de análisis, ver historial, gestionar datos personales/GDPR.

### 3.2 Tecnologías y Arquitectura
- **3.2.1 Evaluación de herramientas y tecnologías disponibles**: aquí replica el estilo de la sección 3.3 de la tesis de referencia ("Librerías y entornos de ejecución") — una lista con versión exacta de cada tecnología. Tu README y `docker-compose.yml` ya tienen esta info; solo hay que formalizarla en una tabla. Justifica cada elección (por qué PostgreSQL y no MySQL, por qué FastAPI/Flask/Django, por qué PyTorch o TensorFlow, por qué contenedores Docker).
- **3.2.2 Propuesta de arquitectura de software**: aquí van tus **diagramas de arquitectura** (ver sección 6 de esta guía). Este es el equivalente a los capítulos 3.1/3.2 de la tesis de referencia sobre arquitectura Turing/Blackwell (hardware GPU) — en tu caso, describe si entrenas localmente con GPU o en la nube, y qué llevó a esa decisión (ej. limitaciones de cómputo, Google Colab, etc.), igual de honesto que el ejemplo, que documentó hasta los problemas de hardware (tarjeta de video dañada, migración de TensorFlow a PyTorch por incompatibilidad CUDA). **Si tuviste contratiempos similares (falta de GPU, cambios de librería, migración de framework), documéntalos — le da rigor y honestidad académica al capítulo.**

---

## 5. Capítulo 4: Desarrollo del Proyecto (el capítulo más largo — ver sección 7 con el orden sugerido)

Este es el corazón de la tesis, igual que en el ejemplo (su Capítulo 4 tiene ~70 páginas). Sigue tu plan de contenido, pero con esta profundidad mínima por sección:

### 4.1 Requisitos funcionales / 4.2 Requisitos no funcionales
Tabla con ID (RF-01, RF-02...), descripción, prioridad. No funcionales: rendimiento (tiempo de respuesta del análisis), seguridad (cifrado, censura de datos sensibles), usabilidad, escalabilidad, disponibilidad.

### 4.3 Desarrollo y construcción / 4.4 Base de datos
Ya tienes este trabajo prácticamente listo en `docs/doc_tesis.md` — es tu documentación del esquema relacional (tablas `users`, `skin_profiles`, `analyses`, `routines`, `products`, etc.). **Reutiliza ese documento directamente como base de esta sección**, adaptando el tono a tesis (quitar encabezados tipo README, mantener las tablas de columnas y el diagrama entidad-relación).

### 4.5 Backend
Sigue el mismo patrón narrativo que el Capítulo 4 del ejemplo (que documentó paso a paso: análisis exploratorio de datos → feature engineering → iteraciones de modelos → resultados), pero adaptado a visión por computador:

- **4.5.1 Recolección de datos**: de dónde viene tu dataset (ej. HAM10000, datasets públicos de dermatología, o dataset propio recolectado). Documenta cantidad de imágenes, clases, distribución (balanceada/desbalanceada), formato, resolución.
- **4.5.2 Preprocesamiento de datos**: aquí van: detección/recorte de rostro, censura de ojos/labios, normalización, aumentación de datos (data augmentation: rotación, flip, brillo), redimensionado. Documenta cada técnica con una imagen antes/después, igual que el ejemplo mostró "feature engineering" con capturas de código y gráficas.
- **4.5.3 Clasificación de imágenes**: aquí documenta **cada iteración del modelo** como hizo el ejemplo con LSTMv1, v2, DeepLSTM, BaseLSTM, FlexLSTM. Tu equivalente sería, por ejemplo:
  - Iteración 1: modelo base/simple (ej. CNN pequeña desde cero) — resultados pobres, ¿por qué?
  - Iteración 2: transfer learning con un modelo preentrenado congelado — mejora.
  - Iteración 3: fine-tuning de capas superiores.
  - Iteración 4: optimización de hiperparámetros (learning rate, batch size, arquitectura) — aquí puedes usar Optuna igual que el ejemplo, o Keras Tuner/Ray Tune si usas TensorFlow.
  - Cada iteración con su tabla de arquitectura (capas, parámetros) y sus métricas (accuracy, loss, matriz de confusión).
- **4.5.4 Categorización de datos**: mapeo de clases predichas a categorías de afecciones y su relación con el motor de recomendación de ingredientes/rutinas.

### 4.6 Frontend
- **4.6.1 Generación de reporte**: cómo se le presenta el resultado al usuario (mockup/captura de pantalla de la interfaz de resultados, similar a cómo el ejemplo mostró sus gráficas de resultados finales).

### 4.7 Diseño del proyecto
- **4.7.1 Estructura del sistema**: diagrama de arquitectura general (ver sección 6).
- **4.7.2 Diseño de base de datos**: diagrama ER (ya lo tienes en `doc_tesis.md`).
- **4.7.3 Diseño de interfaz web**: wireframes o capturas reales de cada pantalla clave (login, carga de imagen, resultados, historial).

### 4.8 Integración del backend y frontend
Diagrama de secuencia (ver sección 6) mostrando el flujo completo: usuario sube imagen → backend detecta/recorta rostro → censura → modelo predice → motor de recomendación → respuesta al frontend → guardado en historial.

> **Sugerencia adicional inspirada en el ejemplo**: al final del Capítulo 4 (antes de pasar a Pruebas), agrega una sección de **"Hallazgos transversales"** (como hizo la tesis de referencia en su 4.6). Ahí resumes en 4-6 bullets las lecciones aprendidas que no encajan en ninguna subsección específica (ej. "el balanceo de clases fue más determinante que la arquitectura", "las imágenes con mala iluminación degradan fuertemente la predicción", etc.). Es un cierre que da mucho valor académico y es fácil de escribir porque ya lo viviste.

---

## 6. Capítulo 5: Pruebas y Validación

- **5.1 Pruebas funcionales y no funcionales**
  - 5.1.1 Pruebas de precisión de modelos de clasificación: reporta accuracy, recall, F1, AUC-ROC por clase, con matriz de confusión. Compara contra un baseline (ej. clasificador aleatorio o el modelo más simple de tus iteraciones), tal como el ejemplo comparó siempre contra "Buy & Hold" o contra el azar de 50%.
  - 5.1.2 Pruebas de estrés (carga concurrente de imágenes/usuarios)
  - 5.1.3 Pruebas de seguridad (inyección, autenticación, manejo de datos sensibles/GDPR)
  - 5.1.4 Pruebas de rendimiento (latencia de inferencia del modelo, tiempo de carga de la app)
- **5.2 Pruebas de usuario**: aquí implementa lo que prometiste en el anteproyecto (formularios de usabilidad con usuarios reales). Reporta resultados cuantitativos (ej. escala SUS, o simplemente % de tareas completadas sin ayuda) — 5.2.1 Eficacia, 5.2.2 Eficiencia, 5.2.3 Precisión (percibida por el usuario vs. real).
- **5.3 Análisis de resultados**: conecta los resultados con la hipótesis/objetivos del Capítulo 1. Sé honesto si algo no funcionó como esperabas — el ejemplo dedica buena parte de sus resultados a explicar **por qué** ciertos enfoques no mejoraron el modelo (ej. "el sentimiento no mejora NVDA porque el mercado ya lo incorpora"); tu equivalente sería explicar por qué cierta clase se confunde más, o por qué cierta técnica de preprocesamiento no ayudó.

---

## 7. (Opcional/recomendado) Capítulo 6: Futuras mejoras

Aunque tu plan de contenido actual no lo tiene como capítulo separado, la tesis de referencia demuestra que es un cierre muy valorado por los asesores. Puedes:
- Insertarlo como Capítulo 6 (pide autorización a tu asesora si implica modificar el plan de contenido aprobado), o
- Insertarlo como sección final del Capítulo 5 ("5.4 Futuras mejoras").

Contenido sugerido: ampliar el dataset, cubrir más tipos de piel/tonos (fairness/sesgo del modelo — tema muy relevante en dermatología por sesgos raciales documentados en la literatura), migrar a app móvil, agregar telemedicina real con dermatólogos, mejorar el motor de recomendación con NLP sobre ingredientes.

---

## 8. Cierre del documento

1. **Conclusiones**: una por objetivo específico, más una conclusión general sobre si se cumplió el objetivo general. Tono breve y reflexivo (mira el estilo corto y personal de las Conclusiones del ejemplo — no es una repetición de resultados, es una reflexión).
2. **Recomendaciones**: dirigidas al lector/usuario final (ej. "no sustituir la consulta médica"), y opcionalmente a futuros desarrolladores del proyecto.
3. **Referencias bibliográficas**: formato APA/IEEE consistente (el ejemplo usa un estilo tipo IEEE numerado con corchetes en el anteproyecto y APA con autor-fecha en la tesis final — **usa el mismo formato en todo el documento**, verifica con tu asesora cuál exige la UTP para el documento final).
4. **Anexos**: capturas adicionales, código relevante, formularios de consentimiento/GDPR usados en las pruebas de usuario, resultados extendidos de matrices de confusión por clase, etc.

---

## 9. Diagramas que deberías tener sí o sí

Basado en lo que usó la tesis de referencia + lo que es obligatorio para un proyecto de software con interfaz + modelo de IA:

| # | Diagrama | Dónde va | Equivalente en el ejemplo |
|---|---|---|---|
| 1 | Diagrama de casos de uso (UML) | Cap. 3.1.2 | No existe en el ejemplo (es específico de apps con usuario) |
| 2 | Diagrama de arquitectura general del sistema (frontend/backend/BD/modelo IA) | Cap. 3.2.2 y 4.7.1 | Ilustración 2 "Diagrama del framework" |
| 3 | Diagrama de secuencia (flujo usuario → resultado) | Cap. 4.8 | Ilustración 3 "Diagrama de secuencia del framework" |
| 4 | Diagrama entidad-relación de la base de datos | Cap. 4.4 y 4.7.2 | (implícito, tú ya lo tienes en `doc_tesis.md`) |
| 5 | Diagrama de clases (backend, o de la librería/framework de detección facial usada) | Cap. 4.5 | Ilustración 4 "Diagrama de clases de yfinance" |
| 6 | Diagrama de despliegue (Docker, contenedores, servicios) | Cap. 3.2.2 | No existe en el ejemplo — agrégalo, tienes `docker-compose.yml` real |
| 7 | Diagrama de arquitectura de la red neuronal (capas por iteración, en tabla + diagrama) | Cap. 4.5.3 | Tablas 2–5 y 9 (arquitecturas LSTM) |
| 8 | Curvas de entrenamiento (loss/accuracy por época, train vs. val) | Cap. 4.5.3 | Ilustraciones 30, 38, 40 (curvas de pérdida) |
| 9 | Matriz de confusión y curva ROC-AUC | Cap. 4.5.3 y 5.1.1 | (equivalente conceptual a las métricas RMSE/MAPE/DA del ejemplo) |
| 10 | Comparación de arquitecturas/modelos candidatos (barras) | Cap. 4.5.3 | Ilustraciones 29, 34, 35 |
| 11 | Wireframes/mockups o capturas de la interfaz real | Cap. 4.6, 4.7.3 | No aplica al ejemplo (no tiene UI) — usa tus capturas reales del frontend |
| 12 | Diagrama de flujo del preprocesamiento de imagen (recorte, censura, regiones) | Cap. 4.5.2 | Ilustración 13 "Feature engineering" (equivalente conceptual) |
| 13 | Cronograma/Gantt actualizado | Anexos o Cap. 3 | Cronograma del anteproyecto (actualízalo con fechas reales) |

---

## 10. Tablas que deberías tener sí o sí

- Tabla de requisitos funcionales y no funcionales (Cap. 4.1–4.2)
- Tabla de tecnologías/versiones exactas de software (Cap. 3.2.1) — parte de esto ya está en tu sección "Herramientas por utilizar" del anteproyecto
- Tabla de hardware usado (ya la tienes en el anteproyecto — actualízala con el hardware final, especialmente si entrenaste en GPU/nube)
- Tabla comparativa de modelos preentrenados candidatos (ResNet/EfficientNet/MobileNet/VGG) con criterios (tamaño, velocidad de inferencia, accuracy reportada en literatura)
- Tabla de composición del dataset (clases, cantidad de imágenes por clase, train/val/test split)
- Tabla de arquitectura por cada iteración del modelo (igual que Tablas 2–5 y 9 del ejemplo)
- Tabla de métricas finales por clase (precision, recall, F1, soporte)
- Tabla de resultados de pruebas de usabilidad

---

## 11. Orden sugerido de redacción (no es el orden final del documento)

Escribir de forma lineal (Cap. 1 → 5) suele ser ineficiente porque el Capítulo 4 es el que más cambia mientras se sigue desarrollando el proyecto. Sugerencia de orden real de trabajo:

1. **Ahora mismo**: mientras programas, ve documentando cada decisión técnica en un archivo de notas (igual como quedó registrado en `docs/doc_tesis.md` para la base de datos). Cuando termines el modelo y el sistema, ya tendrás el 60% del Capítulo 4 escrito en borrador.
2. **Capítulo 3** (Metodología y Arquitectura): escríbelo tan pronto tengas la arquitectura técnica decidida (stack, BD, framework de IA) — no necesitas esperar a terminar el desarrollo.
3. **Capítulo 4** (Desarrollo): a medida que cierres cada módulo (BD → backend de preprocesamiento → modelo → frontend → integración), redacta esa sección de inmediato, con capturas y tablas frescas. Cierra con "Hallazgos transversales".
4. **Capítulo 5** (Pruebas y Validación): solo se puede escribir con el sistema funcionando end-to-end. Es lo último del cuerpo técnico.
5. **Capítulo 2** (Marco Teórico): puedes escribirlo en paralelo desde ya, revisando y ampliando tus referencias del anteproyecto — no depende del avance del desarrollo.
6. **Capítulo 1** (Planteamiento): revisa y "madura" el que ya tienes del anteproyecto, una vez sepas los resultados reales (a veces el problema se termina de entender mejor después de resolverlo).
7. **Futuras mejoras**: se escribe casi solo si llevaste una lista de "cosas que no hice pero pensé" durante el desarrollo.
8. **Conclusiones y Recomendaciones**: al final, una vez tengas resultados de las pruebas.
9. **Páginas preliminares** (Resumen, Dedicatoria, Agradecimientos, Índices, Introducción general): literalmente lo último, cuando ya sabes la paginación final y el tono general de lo que escribiste.
10. **Revisión de referencias y anexos**: al cierre, verificando formato consistente (APA o IEEE, no mezclar) y que cada figura/tabla tomada de otra fuente tenga su cita (ver advertencia abajo).

---

## 12. Advertencias/lecciones tomadas directamente de los errores marcados por el asesor en el ejemplo

En la tesis de referencia, el asesor dejó comentarios señalando fallas puntuales. Evítalas desde el principio:

1. **Toda figura que no sea tuya necesita cita explícita de fuente** (el asesor marcó una figura de un libro sin referencia — "esta figura de dónde salió, parece un libro, hay que poner la referencia"). Si usas un diagrama, ícono o imagen de un modelo preentrenado, arquitectura de red conocida (ej. diagrama de ResNet), o captura de otra app (screenshots de competidores para "antecedentes"), **cita la fuente debajo de la imagen igual que citas texto**.
2. **Toda tabla mencionada en el texto debe estar realmente insertada** (el asesor marcó "Tabla 1... esta tabla no se refleja en el texto, debes insertarlo" — es decir, se mencionó una tabla que no aparecía). Verifica que cada `Tabla X` / `Ilustración X` que citas en el texto exista físicamente cerca de esa mención.
3. **No dejes títulos de sección sin contenido** (el asesor marcó un encabezado vacío con solo "sección"). Cada subtítulo debe tener al menos un párrafo introductorio antes de pasar al siguiente subnivel.
4. **Numeración de ilustraciones y tablas consecutiva y sin saltos**, actualizando el índice de figuras/tablas al final, no a medida que escribes (es más fácil generar el índice cuando el documento ya está cerrado).
5. **Consistencia en cursivas de términos en inglés** (el ejemplo usa cursiva consistente para *software*, *dataset*, *feature engineering*, *backend*, *frontend*, *deep learning*, etc.). Decide desde el inicio una lista de anglicismos que irán en cursiva y aplícala en todo el documento.

---

## 13. Checklist final antes de entregar

- [ ] Todas las figuras citadas en el texto existen y están numeradas correctamente.
- [ ] Todas las tablas citadas en el texto existen y están numeradas correctamente.
- [ ] Cada objetivo específico del Cap. 1 tiene una sección correspondiente en el Cap. 4 que demuestra su cumplimiento.
- [ ] El Capítulo 5 contiene métricas cuantitativas reales (no solo capturas de pantalla).
- [ ] Las conclusiones responden directamente a los objetivos, no repiten el resumen.
- [ ] Las referencias están en un solo formato (APA o IEEE) en todo el documento.
- [ ] Se incluye al menos una recomendación ética clara (no reemplazo del criterio médico).
- [ ] El índice general, de figuras y de tablas coincide exactamente con la numeración de página final.
- [ ] Todo el código/arquitectura descrito en el Cap. 4 coincide con lo implementado realmente (revisa contra `docs/doc_tesis.md`, `README.md` y `DOCUMENTACION_TECNICA.md` del repo para no contradecirte).

---

## 14. Distribución sugerida de páginas por capítulo (para ~100 páginas de contenido)

"Páginas de contenido" = solo el cuerpo numerado en arábigos (Capítulos 1 al 5/6). **No** incluye páginas preliminares (portada, resumen, dedicatoria, índices — numeradas en romanos), ni Referencias ni Anexos, que se cuentan aparte.

Como referencia real: en la tesis de ejemplo, de la página 2 a la 103 (~102 páginas de cuerpo), la distribución fue Cap.1 ≈20 pág., Cap.2 ≈8 pág., Cap.3 ≈5 pág., Cap.4 ≈67 pág. (66% del total), Cap.5 ≈2 pág. El patrón se repite en la mayoría de tesis de Ingeniería de Software: **el capítulo de Desarrollo domina el documento**, todo lo demás es proporcionalmente corto.

Aplicando esa misma lógica a tu estructura de 5 capítulos (más un Cap. 6 opcional de Futuras mejoras) sobre 100 páginas:

| Capítulo | Páginas sugeridas | % del total | Justificación |
|---|---|---|---|
| Cap. 1 — Planteamiento del problema | 8–10 | ~9% | Problemática, propuesta, objetivos, alcance e impacto social no requieren mucha extensión; es contextual, no técnico. |
| Cap. 2 — Marco Teórico | 12–15 | ~13% | Necesitas espacio para explicar CNN, transfer learning, detección facial, métricas y ética/anonimización con nivel de detalle técnico, más antecedentes de 4–6 trabajos relacionados. |
| Cap. 3 — Metodología de Trabajo | 8–10 | ~9% | Metodología de gestión, casos de uso, evaluación de tecnologías y arquitectura general — es descriptivo, no necesita extenderse tanto como el Cap. 4. |
| Cap. 4 — Desarrollo del Proyecto | 48–55 | ~50% | Es el núcleo del documento: dataset, preprocesamiento, iteraciones del modelo (cada una con tabla + figura), base de datos, backend, frontend, integración, hallazgos transversales. |
| Cap. 5 — Pruebas y Validación | 12–15 | ~13% | Métricas finales, pruebas funcionales/no funcionales, pruebas de usuario con datos reales y análisis de resultados. |
| Cap. 6 — Futuras mejoras (opcional, o como 5.4) | 2–4 | ~3% | Sección de cierre corta, igual que en el ejemplo (apenas 2 páginas). |
| **Total** | **~100** | **100%** | |

### Desglose interno sugerido del Capítulo 4 (por ser el más grande, es el que más fácil se desborda o se queda corto)

| Sección | Páginas aprox. |
|---|---|
| 4.1–4.2 Requisitos funcionales/no funcionales | 3–4 |
| 4.3–4.4 Desarrollo, construcción y base de datos | 6–8 |
| 4.5 Backend (recolección, preprocesamiento, iteraciones del modelo, categorización) | 20–24 |
| 4.6 Frontend (interfaz y generación de reporte) | 5–6 |
| 4.7 Diseño del proyecto (estructura, BD, interfaz web) | 6–8 |
| 4.8 Integración backend/frontend + hallazgos transversales | 4–5 |

### Cómo usar estos números

- Son **rangos orientativos**, no un límite rígido — sirven para detectar a tiempo si un capítulo se está quedando muy corto (señal de que falta profundidad) o demasiado largo (señal de que hay contenido que debería moverse a Anexos, como capturas extensas de código o tablas de resultados muy detalladas).
- Si tu asesora exige un mínimo distinto de páginas totales, escala las proporciones (%) en lugar de los números fijos.
- El Cap. 4 es el único que vale la pena revisar sección por sección con el desglose de arriba, porque ahí es donde documentar cada iteración del modelo (ver sección 5 de esta guía) puede crecer sin control si no se resume con tablas comparativas en vez de repetir gráficas casi idénticas.

---

## 15. Resumen de diagramas necesarios

Tabla de referencia rápida (ya detallada en la sección 9) con todos los diagramas obligatorios y dónde ubicarlos:

| # | Diagrama | Dónde va | Equivalente en el ejemplo |
|---|---|---|---|
| 1 | Diagrama de casos de uso (UML) | Cap. 3.1.2 | No existe en el ejemplo (es específico de apps con usuario) |
| 2 | Diagrama de arquitectura general del sistema (frontend/backend/BD/modelo IA) | Cap. 3.2.2 y 4.7.1 | Ilustración 2 "Diagrama del framework" |
| 3 | Diagrama de secuencia (flujo usuario → resultado) | Cap. 4.8 | Ilustración 3 "Diagrama de secuencia del framework" |
| 4 | Diagrama entidad-relación de la base de datos | Cap. 4.4 y 4.7.2 | (implícito, tú ya lo tienes en `doc_tesis.md`) |
| 5 | Diagrama de clases (backend, o de la librería/framework de detección facial usada) | Cap. 4.5 | Ilustración 4 "Diagrama de clases de yfinance" |
| 6 | Diagrama de despliegue (Docker, contenedores, servicios) | Cap. 3.2.2 | No existe en el ejemplo — agrégalo, tienes `docker-compose.yml` real |
| 7 | Diagrama de arquitectura de la red neuronal (capas por iteración, en tabla + diagrama) | Cap. 4.5.3 | Tablas 2–5 y 9 (arquitecturas LSTM) |
| 8 | Curvas de entrenamiento (loss/accuracy por época, train vs. val) | Cap. 4.5.3 | Ilustraciones 30, 38, 40 (curvas de pérdida) |
| 9 | Matriz de confusión y curva ROC-AUC | Cap. 4.5.3 y 5.1.1 | (equivalente conceptual a las métricas RMSE/MAPE/DA del ejemplo) |
| 10 | Comparación de arquitecturas/modelos candidatos (barras) | Cap. 4.5.3 | Ilustraciones 29, 34, 35 |
| 11 | Wireframes/mockups o capturas de la interfaz real | Cap. 4.6, 4.7.3 | No aplica al ejemplo (no tiene UI) — usa tus capturas reales del frontend |
| 12 | Diagrama de flujo del preprocesamiento de imagen (recorte, censura, regiones) | Cap. 4.5.2 | Ilustración 13 "Feature engineering" (equivalente conceptual) |
| 13 | Cronograma/Gantt actualizado | Anexos o Cap. 3 | Cronograma del anteproyecto (actualízalo con fechas reales) |
