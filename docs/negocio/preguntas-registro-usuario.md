# Preguntas al usuario durante el registro

Documento que describe todos los campos y preguntas presentadas al usuario a lo largo del flujo de registro y configuración de perfil.

---

## Fase 1 — Registro inicial

**Archivo:** [frontend/src/pages/auth.html](../frontend/src/pages/auth.html)  
**Lógica:** [frontend/src/scripts/auth.js](../frontend/src/scripts/auth.js)

| Campo | Etiqueta | Tipo | Placeholder | Reglas de validación |
|-------|----------|------|-------------|----------------------|
| `reg-name` | Nombre completo | texto | María García | Requerido |
| `reg-email` | Correo electrónico | email | maria@email.com | Requerido · formato de email válido |
| `reg-pw` | Contraseña | contraseña | •••••••• | Requerido · mínimo 8 caracteres |
| `reg-pw2` | Confirmar contraseña | contraseña | •••••••• | Requerido · debe coincidir con la contraseña |
| `reg-consent` | Acepto los términos de uso y el tratamiento de mis datos | checkbox | — | Requerido |

### Mensajes de error

- "Completa todos los campos."
- "La contraseña debe tener al menos 8 caracteres."
- "Las contraseñas no coinciden."
- "Debes aceptar los términos para continuar."
- "El correo ya está registrado."
- "Error al registrarse."

---

## Fase 2 — Configuración del perfil de piel

**Archivo:** [frontend/src/pages/profile.html](../frontend/src/pages/profile.html)  
**Lógica:** [frontend/src/scripts/profile.js](../frontend/src/scripts/profile.js)

---

### Sección 1 — Datos básicos

| Campo | Pregunta | Tipo | Opciones / Rango | Validación |
|-------|----------|------|------------------|------------|
| `age` | ¿Cuántos años tienes? | número | 12 – 90 | Requerido · "Ingresa una edad válida (12-90 años)." |
| `sex` | Sexo biológico | botones | Masculino · Femenino | Requerido |

---

### Sección 2 — Fototipo de Fitzpatrick

**Pregunta:** ¿Cómo reacciona tu piel al sol sin protector?

| Valor | Descripción |
|-------|-------------|
| I | Siempre se quema, nunca se broncea |
| II | Casi siempre se quema, broncea poco |
| III | A veces se quema, se broncea gradualmente |
| IV | Raramente se quema, siempre se broncea |
| V | Muy raramente se quema, se broncea intensamente |
| VI | Nunca se quema, piel muy pigmentada |
| Desconocido | No sé cómo reacciona mi piel al sol |

---

### Sección 3 — Tipo de piel

**Pregunta implícita:** ¿Qué tipo de piel tienes?

Opciones (selección única):

- Grasa
- Mixta
- Seca
- Sensible
- Normal
- No sé qué tipo de piel tengo

---

### Sección 4 — Historial dermatológico

**Pregunta implícita:** ¿Tienes o has tenido alguna de estas condiciones? *(selección múltiple)*

- Acné
- Rosácea
- Dermatitis
- Psoriasis
- Eccema
- Ninguna

**Pregunta adicional:** ¿Has recibido tratamiento previo?

- Sí
- No

---

### Sección 5 — Alergias a ingredientes

**Pregunta:** ¿Tienes alergias a algún ingrediente cosmético?

- Sí
- No
- No sé

> Si la respuesta es **Sí**, se muestra un campo de texto adicional:
>
> **¿A qué ingredientes?** — Placeholder: *"Ej: fragancia, parabenos..."*

---

### Sección 6 — Zona geográfica

| Campo | Pregunta | Tipo | Opciones |
|-------|----------|------|----------|
| `country` | País | desplegable | Panamá · México · Colombia · Argentina · Costa Rica · Guatemala · Perú · Chile · Venezuela · Otro |
| `city` | Ciudad | texto | Placeholder: *"Ciudad de Panamá"* |

**Pregunta adicional:** ¿Pasas tiempo en espacios con aire acondicionado o calefacción?

- Sí, siempre
- A veces
- No

---

## Resumen del flujo completo

```
1. Registro
   └── Nombre · Email · Contraseña · Aceptar términos

2. Perfil de piel
   ├── Edad y sexo biológico
   ├── Fototipo de Fitzpatrick (I–VI)
   ├── Tipo de piel
   ├── Historial dermatológico + tratamiento previo
   ├── Alergias a ingredientes
   └── País · Ciudad · Exposición a A/C o calefacción
```

---

## Archivos relevantes

| Componente | Ruta |
|------------|------|
| Formulario de registro (HTML) | [frontend/src/pages/auth.html](../frontend/src/pages/auth.html) |
| Lógica de registro | [frontend/src/scripts/auth.js](../frontend/src/scripts/auth.js) |
| Formulario de perfil (HTML) | [frontend/src/pages/profile.html](../frontend/src/pages/profile.html) |
| Lógica de perfil | [frontend/src/scripts/profile.js](../frontend/src/scripts/profile.js) |
| Endpoints de autenticación | [backend/app/api/auth.py](../backend/app/api/auth.py) |
| Endpoints de usuario | [backend/app/api/users.py](../backend/app/api/users.py) |
| Modelos de base de datos | [backend/app/models.py](../backend/app/models.py) |
| Esquemas Pydantic | [backend/app/schemas.py](../backend/app/schemas.py) |
