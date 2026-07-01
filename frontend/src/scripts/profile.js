/**
 * profile.js
 * Lógica del formulario de perfil de piel.
 * Conectado a POST /api/users/profile.
 */

const API = '/api'

const CITIES_BY_COUNTRY = {
  panama:     ['Ciudad de Panamá', 'San Miguelito', 'Colón', 'David', 'La Chorrera', 'Arraiján', 'Penonomé', 'Santiago', 'Chitré', 'Bocas del Toro'],
  mexico:     ['Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana', 'León', 'Ciudad Juárez', 'Mérida', 'Querétaro', 'Cancún', 'Zapopan', 'San Luis Potosí'],
  colombia:   ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Cúcuta', 'Bucaramanga', 'Pereira', 'Santa Marta', 'Ibagué', 'Manizales'],
  argentina:  ['Buenos Aires', 'Córdoba', 'Rosario', 'Mendoza', 'La Plata', 'Tucumán', 'Mar del Plata', 'Salta', 'Santa Fe', 'San Juan', 'Resistencia'],
  costa_rica: ['San José', 'Alajuela', 'Desamparados', 'Heredia', 'Cartago', 'Liberia', 'Pérez Zeledón', 'San Carlos', 'Puntarenas', 'Limón'],
  guatemala:  ['Ciudad de Guatemala', 'Mixco', 'Villa Nueva', 'Quetzaltenango', 'San Juan Sacatepéquez', 'Cobán', 'Escuintla', 'Jalapa', 'Huehuetenango', 'Chiquimula'],
  peru:       ['Lima', 'Arequipa', 'Trujillo', 'Chiclayo', 'Iquitos', 'Piura', 'Cusco', 'Huancayo', 'Chimbote', 'Tacna', 'Pucallpa'],
  chile:      ['Santiago', 'Puente Alto', 'Antofagasta', 'Viña del Mar', 'Valparaíso', 'Concepción', 'Temuco', 'Rancagua', 'Talca', 'Arica', 'Iquique'],
  venezuela:  ['Caracas', 'Maracaibo', 'Valencia', 'Barquisimeto', 'Maracay', 'Ciudad Guayana', 'San Cristóbal', 'Maturín', 'Cumaná', 'Mérida', 'Barinas'],
}

const FITZ_LABELS = {
  I:   'Tipo I — Siempre se quema, nunca se broncea',
  II:  'Tipo II — Casi siempre se quema, broncea poco',
  III: 'Tipo III — A veces se quema, se broncea gradualmente',
  IV:  'Tipo IV — Raramente se quema, siempre se broncea',
  V:   'Tipo V — Muy raramente se quema, se broncea intensamente',
  VI:  'Tipo VI — Nunca se quema, piel muy pigmentada',
}

export function initProfile() {
  if (localStorage.getItem('cutislab_profile_complete') === '1') {
    document.getElementById('btn-back-profile')?.classList.remove('hidden')
  } else {
    const btnBackAuth = document.getElementById('btn-back-auth')
    if (btnBackAuth) {
      btnBackAuth.classList.remove('hidden')
      btnBackAuth.addEventListener('click', () => {
        localStorage.removeItem('cutislab_token')
        localStorage.removeItem('cutislab_user')
        localStorage.removeItem('cutislab_profile_complete')
        window.goAuth('login')
      })
    }
  }
  initFitzpatrickInteraction()
  initMultiSelect()
  initAllergyExclusion()
  initCitySelect()
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

function initCitySelect() {
  const countryEl  = document.getElementById('country')
  const citySelect = document.getElementById('city')
  const cityOther  = document.getElementById('city-other')
  if (!countryEl || !citySelect || !cityOther) return

  countryEl.addEventListener('change', () => {
    const country = countryEl.value
    const cities  = CITIES_BY_COUNTRY[country]

    if (!country) {
      citySelect.innerHTML  = '<option value="">Selecciona primero un país</option>'
      citySelect.disabled   = true
      citySelect.classList.remove('hidden')
      cityOther.classList.add('hidden')
      return
    }

    if (country === 'otro') {
      citySelect.classList.add('hidden')
      cityOther.classList.remove('hidden')
      cityOther.value = ''
      return
    }

    citySelect.classList.remove('hidden')
    cityOther.classList.add('hidden')
    citySelect.disabled  = false
    citySelect.innerHTML = '<option value="">Selecciona una ciudad</option>' +
      cities.map(c => `<option value="${c}">${c}</option>`).join('')
  })
}

function initAllergyExclusion() {
  const allergyBtns = document.querySelectorAll('[data-group="allergy"]')
  allergyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.dataset.value === 'none') {
        // "No tengo alergias" seleccionado: desmarcar las específicas
        allergyBtns.forEach(b => { if (b.dataset.value !== 'none') b.classList.remove('selected') })
      } else {
        // Alergia específica seleccionada: desmarcar "No tengo alergias"
        document.querySelector('[data-group="allergy"][data-value="none"]')?.classList.remove('selected')
      }
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
    const city         = (country === 'otro'
      ? document.getElementById('city-other')
      : document.getElementById('city'))?.value?.trim()
    const conditions   = [...document.querySelectorAll('[data-group="cond"].selected')].map(b => b.dataset.value)
    const allergies    = [...document.querySelectorAll('[data-group="allergy"].selected')]
                          .map(b => b.dataset.value)
                          .filter(v => v !== 'none')

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
      allergies,
      country:         country      || null,
      city:            city         || null,
    }

    btn.disabled    = true
    btn.textContent = 'Guardando...'
    hideMsg(errorBox)
    hideMsg(successBox)

    try {
      const token = localStorage.getItem('cutislab_token')
      const res   = await fetch(`${API}/users/profile`, {
        method:  'PUT',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al guardar el perfil.')

      // Actualizar localStorage con los datos del perfil para que account.js los lea
      const user = JSON.parse(localStorage.getItem('cutislab_user') || '{}')
      Object.assign(user, profileData)
      localStorage.setItem('cutislab_user', JSON.stringify(user))

      localStorage.setItem('cutislab_profile_complete', '1')
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
