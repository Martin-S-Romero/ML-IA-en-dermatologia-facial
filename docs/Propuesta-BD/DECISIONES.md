# Decisiones de Implementación — Propuesta-BD

Evaluación de qué propuestas de `docs/Propuesta-BD/` se implementan en el
motor de recomendación y cuáles se descartan, con justificación breve.

Referencias:
- [lesiones-investigacion-cientifica.md](lesiones-investigacion-cientifica.md) — Base clínica científica
- [propuesta-estructura-lesion.md](propuesta-estructura-lesion.md) — Esquema SQL relacional
- [propuesta-final-explicacion.md](propuesta-final-explicacion.md) — Arquitectura unificada

---

## ✅ VA — Ingredientes a BD (Opción A)

**Qué es:** Mover los diccionarios `FALLBACK_TARGET` / `FALLBACK_AVOID` hardcodeados
en `recommendation_engine.py` a dos tablas SQL:
- `condition_target_ingredients(condition TEXT, ingredient_name TEXT)`
- `condition_avoid_ingredients(condition TEXT, ingredient_name TEXT, reason TEXT)`

**Por qué sí:** Permite editar qué ingredientes aplican a cada condición sin tocar
código Python. El equipo puede actualizar las listas desde SQL sin redeploy.
Complejidad baja (2 tablas, seed con los mismos datos actuales).

---

## ✅ VA — Alergias booleanas en skin_profiles (Opción B)

**Qué es:** Agregar columnas booleanas a `skin_profiles`:
`allergy_fragrance`, `allergy_paraben`, `allergy_salicylic_acid`,
`allergy_lanolin`, `allergy_benzoyl_peroxide`.

**Por qué sí:** Personalización real y directa. Si el usuario marca
`allergy_fragrance=true`, el engine excluye automáticamente productos
con fragancia antes del scoring. Bajo costo (una migración + campo en formulario).

---

## ❌ NO VA — Índice comedogénico en ingredients (Opción C)

**Qué es:** Agregar `comedogenic_index` (0-5, escala Kligman) a la tabla
`ingredients` para penalizar o excluir productos en perfiles con piel grasa / acné.

**Por qué no:** La columna `irr_com` ya existe en `product_ingredients` pero tiene
69% de valores NULL y 11k+ registros malformados (ej. `"0-3, 0-3"`).
Agregar otro campo de comedogenicidad sin datos confiables llevaría a penalizar
siempre los mismos 30% de productos con datos, sesgando todas las demás
recomendaciones hacia productos sin información. El resultado sería
peor que el estado actual.

---

## ❌ NO VA (ahora) — condition_phases (active / healing / maintenance)

**Qué es:** Nueva tabla `condition_phases` + campo en `routines` y `analyses`
para contextualizar las recomendaciones según la fase de evolución de la condición.

**Por qué no ahora:** La detección de fase requiere que el modelo IA la produzca
o que el usuario la reporte explícitamente. Sin esa entrada, las fases son
decorativas — no cambian las recomendaciones reales. Alta complejidad para
impacto nulo mientras el modelo no emita `condition_phase_key`.
Reevaluar cuando el modelo v4+ incluya clasificación de fase.

---

## ❌ NO VA — condition_repercussions / condition_symptoms

**Qué es:** Tablas de efectos clínicos esperados (cicatrices, eritema) y
síntomas subjetivos (ardor, picor) por condición.

**Por qué no:** Son datos puramente educativos — no cambian qué productos
se recomiendan ni cómo se ordenan. El impacto en el motor de recomendación
es cero. Útiles para una futura sección de "explicación" en el frontend,
pero no son prioritarios para el scope de la tesis.

---

## ❌ NO VA — treatment_needs / avoid_reasons (tablas clínicas completas)

**Qué es:** Las 10 tablas clínicas completas de `propuesta-estructura-lesion.md`
(condiciones, necesidades terapéuticas, razones de exclusión, etc.).

**Por qué no:** La Opción A ya resuelve el mismo caso de uso (ingredientes
recomendados/evitados por condición) con 2 tablas en vez de 10.
El overhead de definir `avoid_reasons`, `treatment_needs`, etc. no se
justifica en el alcance actual. Puede escalarse en fases futuras.

---

## ⏳ EVALUAR DESPUÉS — analysis_zone_metrics

**Qué es:** Tabla que extrae las métricas por zona facial del JSONB `result`
(eritema, comedones, escamas por zona) para comparar evolución entre análisis.

**Por qué después:** Funcionalidad de alto valor para el seguimiento del
progreso del usuario, pero depende de que el modelo genere datos zonales
confiables y consistentes. Posponer hasta acumular suficientes análisis reales.

---

## ⏳ EVALUAR DESPUÉS — campo `locked` en routines

**Qué es:** Booleano en `routines` para evitar que el motor reemplace toda la
rutina cuando detecta una nueva condición (evita que el usuario descarte
productos que acaba de comprar).

**Por qué después:** No afecta directamente el motor de recomendación de
productos, sino la lógica de gestión de rutinas. Se puede agregar como
feature independiente de rutinas sin bloquear las mejoras actuales del motor.
