/**
 * profile.js
 * Lógica del formulario de perfil de piel.
 * Conectado a POST /api/users/profile.
 */

const API = 'http://localhost:8000/api'

const FITZ_LABELS = {
  I:   'Tipo I — Siempre se quema, nunca se broncea',
  II:  'Tipo II — Casi siempre se quema, broncea poco',
  III: 'Tipo III — A veces se quema, se broncea gradualmente',
  IV:  'Tipo IV — Raramente se quema, siempre se broncea',
  V:   'Tipo V — Muy raramente se quema, se broncea intensamente',
  VI:  'Tipo VI — Nunca se quema, piel muy pigmentada',
}

export function initProfile() {
  // Mostrar "Volver al Dashboard" solo si el perfil ya fue completado antes
  if (localStorage.getItem('skinai_profile_complete') === '1') {
    document.getElementById('btn-back-profile')?.classList.remove('hidden')
  }
  initFitzpatrickInteraction()
  initAllergyToggle()
  initMultiSelect()
  initSaveProfile()
}

function initFitzpatrickInteraction() {
  document.querySelectorAll('.fitz-dot').forEach(dot => {
    dot.addEventListener('click', (e) => {
      e.stopPropagation()  // prevent bindFitzDots (ui.js) from also running
      const wasSelected = dot.classList.contains('selected')
      document.querySelectorAll('.fitz-dot').forEach(d => d.classList.remove('selected'))
      const label = document.getElementById('fitz-label')
      if (wasSelected) {
        if (label) label.textContent = 'Selecciona tu fototipo tocando uno de los colores'
      } else {
        dot.classList.add('selected')
        const val = dot.dataset.value
        if (label && FITZ_LABELS[val]) {
          label.innerHTML = `<strong class="text-ink block mb-0.5">Tipo ${val} seleccionado</strong>${FITZ_LABELS[val]}`
        }
      }
    })
  })
}

function initAllergyToggle() {
  document.querySelectorAll('[data-group="allergy"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = document.getElementById('allergy-input')
      if (input) input.classList.toggle('hidden', btn.dataset.value !== 'si')
    })
  })
}

function initMultiSelect() {
  document.querySelectorAll('.option-btn.multi').forEach(btn => {
    btn.addEventListener('click', () => btn.classList.toggle('selected'))
  })
}

function initSaveProfile() {
  const btn = document.getElementById('btn-save-profile')
  if (!btn) return

  btn.addEventListener('click', async () => {
    const errorBox   = document.getElementById('profile-error')
    const successBox = document.getElementById('profile-success')

    const age          = document.getElementById('age')?.value
    const gender       = document.querySelector('[data-group="sex"].selected')?.dataset.value
    const fitzDot      = document.querySelector('.fitz-dot.selected')?.dataset.value
    const skintype     = document.querySelector('[data-group="skintype"].selected')?.dataset.value
    const country      = document.getElementById('country')?.value
    const city         = document.getElementById('city')?.value.trim()
    const conditions   = [...document.querySelectorAll('[data-group="cond"].selected')].map(b => b.dataset.value)
    const allergy      = document.querySelector('[data-group="allergy"].selected')?.dataset.value
    const allergyDetail = document.getElementById('allergy-detail')?.value.trim()

    if (!age || age < 12 || age > 90) {
      return showMsg(errorBox, successBox, 'Ingresa una edad válida (12-90 años).', 'error')
    }
    if (!gender) {
      return showMsg(errorBox, successBox, 'Selecciona tu sexo biológico.', 'error')
    }

    const profileData = {
      age:             parseInt(age),
      gender,
      skin_type:       skintype     || null,
      fitzpatrick:     fitzDot      || null,
      skin_conditions: conditions,
      allergies:       allergy === 'si' ? [allergyDetail].filter(Boolean) : [],
      country:         country      || null,
      city:            city         || null,
    }

    btn.disabled    = true
    btn.textContent = 'Guardando...'
    hideMsg(errorBox)
    hideMsg(successBox)

    try {
      const token = localStorage.getItem('skinai_token')
      const res   = await fetch(`${API}/users/profile`, {
        method:  'POST',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al guardar el perfil.')

      // Actualizar localStorage con los datos del perfil para que account.js los lea
      const user = JSON.parse(localStorage.getItem('skinai_user') || '{}')
      Object.assign(user, profileData)
      localStorage.setItem('skinai_user', JSON.stringify(user))

      localStorage.setItem('skinai_profile_complete', '1')
      showMsg(successBox, errorBox, 'Perfil guardado correctamente.', 'success')
      setTimeout(() => window._goFull('capture'), 800)

    } catch (err) {
      showMsg(errorBox, successBox, err.message, 'error')
    } finally {
      btn.disabled    = false
      btn.textContent = 'Guardar y continuar →'
    }
  })
}

function showMsg(show, hide, msg) {
  show.textContent = msg
  show.classList.remove('hidden')
  hide.classList.add('hidden')
}

function hideMsg(box) {
  box.textContent = ''
  box.classList.add('hidden')
}
