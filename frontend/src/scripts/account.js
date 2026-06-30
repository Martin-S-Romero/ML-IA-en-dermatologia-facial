/**
 * account.js
 * Carga y edición de los datos de cuenta del usuario.
 * Conectado a GET /api/users/me, GET /api/users/profile y PUT /api/users/me.
 */

const API = 'http://localhost:8000/api'

export function initAccount() {
  loadUserData()
}

async function loadUserData() {
  const token = localStorage.getItem('cutislab_token')

  // Datos básicos del usuario (nombre, email) — vienen del login en localStorage
  const user = JSON.parse(localStorage.getItem('cutislab_user') || '{}')

  setEl('account-avatar',       getInitials(user.full_name))
  setEl('account-name',         user.full_name || '--')
  setEl('account-email',        user.email     || '--')
  setEl('account-email-field',  user.email     || '--')

  // Datos del perfil de piel — fetch desde la API
  try {
    const res = await fetch(`${API}/users/profile`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })

    if (res.ok) {
      const profile = await res.json()

      // Actualizar localStorage con los datos frescos del perfil
      Object.assign(user, {
        age:            profile.age,
        gender:         profile.gender,
        fitzpatrick:    profile.fitzpatrick,
        skin_type:      profile.skin_type,
        allergies:      profile.allergies,
        skin_conditions: profile.skin_conditions,
      })
      localStorage.setItem('cutislab_user', JSON.stringify(user))

      setEl('account-age',       profile.age       ? `${profile.age} años` : '--')
      setEl('account-gender',    capitalize(profile.gender)    || '--')
      setEl('account-fitz',      profile.fitzpatrick ? `Tipo ${profile.fitzpatrick}` : '--')
      setEl('account-skintype',  capitalize(profile.skin_type) || '--')
      setEl('account-allergies', profile.allergies?.length ? profile.allergies.join(', ') : 'Ninguna')
    } else {
      // Sin perfil de piel todavía
      setEl('account-age',       '--')
      setEl('account-gender',    '--')
      setEl('account-fitz',      '--')
      setEl('account-skintype',  '--')
      setEl('account-allergies', '--')
    }
  } catch {
    // Error de red: mostrar lo que haya en localStorage
    setEl('account-age',       user.age       ? `${user.age} años` : '--')
    setEl('account-gender',    capitalize(user.gender)    || '--')
    setEl('account-fitz',      user.fitzpatrick ? `Tipo ${user.fitzpatrick}` : '--')
    setEl('account-skintype',  capitalize(user.skin_type) || '--')
    setEl('account-allergies', user.allergies?.length ? user.allergies.join(', ') : 'Ninguna')
  }

  initEditFields()
}

const FITZ_OPTIONS = [
  ['',    'Seleccionar fototipo...'],
  ['I',   'Tipo I — Siempre se quema, nunca se broncea'],
  ['II',  'Tipo II — Casi siempre se quema, broncea poco'],
  ['III', 'Tipo III — A veces se quema, broncea gradualmente'],
  ['IV',  'Tipo IV — Raramente se quema, siempre se broncea'],
  ['V',   'Tipo V — Muy raramente se quema, broncea intensamente'],
  ['VI',  'Tipo VI — Nunca se quema, piel muy pigmentada'],
]

const SKINTYPE_OPTIONS = [
  ['',            'Seleccionar tipo...'],
  ['grasa',       'Grasa'],
  ['mixta',       'Mixta'],
  ['seca',        'Seca'],
  ['sensible',    'Sensible'],
  ['normal',      'Normal'],
  ['desconocido', 'No sé qué tipo tengo'],
]

const FIELD_STYLE   = 'border:1.5px solid #E8E2D6;border-radius:8px;padding:4px 8px;font-size:12px;outline:none;font-family:inherit;background:#fff;color:#181C24'
const SAVE_STYLE    = 'margin-left:6px;font-size:10px;color:#233D30;background:none;border:none;cursor:pointer;font-weight:600'
const CANCEL_STYLE  = 'margin-left:4px;font-size:10px;color:#5A6474;background:none;border:none;cursor:pointer'
const EDIT_BTN_STYLE = 'margin-left:8px;font-size:10px;color:#B89A72;background:none;border:none;cursor:pointer;text-decoration:underline'

function initEditFields() {
  const fields = [
    { id: 'account-age',       key: 'age'         },
    { id: 'account-fitz',      key: 'fitzpatrick'  },
    { id: 'account-skintype',  key: 'skin_type'    },
    { id: 'account-allergies', key: 'allergies'    },
  ]

  fields.forEach(({ id, key }) => {
    const cell = document.getElementById(id)
    if (!cell) return
    const editBtn = document.createElement('button')
    editBtn.textContent = 'Editar'
    editBtn.style.cssText = EDIT_BTN_STYLE
    editBtn.onclick = () => startEdit(cell, editBtn, key)
    cell.parentElement.appendChild(editBtn)
  })
}

async function startEdit(cell, btn, key) {
  const user   = JSON.parse(localStorage.getItem('cutislab_user') || '{}')
  const rawVal = user[key]

  const control = buildControl(key, rawVal)

  const saveBtn   = document.createElement('button')
  saveBtn.textContent = 'Guardar'
  saveBtn.style.cssText = SAVE_STYLE

  const cancelBtn = document.createElement('button')
  cancelBtn.textContent = 'Cancelar'
  cancelBtn.style.cssText = CANCEL_STYLE

  cell.style.display = 'none'
  btn.style.display  = 'none'
  cell.parentElement.appendChild(control)
  cell.parentElement.appendChild(saveBtn)
  cell.parentElement.appendChild(cancelBtn)
  control.focus?.()

  const restore = () => {
    control.remove(); saveBtn.remove(); cancelBtn.remove()
    cell.style.display = ''; btn.style.display = ''
  }

  cancelBtn.onclick = restore

  saveBtn.onclick = async () => {
    const { apiValue, displayText } = readValue(key, control)
    if (apiValue === null) return

    try {
      const token = localStorage.getItem('cutislab_token')
      const res   = await fetch(`${API}/users/me`, {
        method:  'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body:    JSON.stringify({ [key]: apiValue }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Error al guardar.')
      }

      const stored = JSON.parse(localStorage.getItem('cutislab_user') || '{}')
      stored[key] = apiValue
      localStorage.setItem('cutislab_user', JSON.stringify(stored))

      cell.textContent = displayText

    } catch (err) {
      alert(err.message)
    } finally {
      restore()
    }
  }
}

function buildControl(key, rawVal) {
  if (key === 'fitzpatrick') {
    return buildSelect(FITZ_OPTIONS, rawVal ?? '')
  }
  if (key === 'skin_type') {
    return buildSelect(SKINTYPE_OPTIONS, rawVal ?? '')
  }
  if (key === 'allergies') {
    const inp = document.createElement('input')
    inp.type        = 'text'
    inp.value       = Array.isArray(rawVal) ? rawVal.join(', ') : ''
    inp.placeholder = 'Ej: retinol, parfum, parabenos...'
    inp.style.cssText = FIELD_STYLE + ';max-width:200px'
    return inp
  }
  // age
  const inp = document.createElement('input')
  inp.type      = 'number'
  inp.value     = rawVal ?? ''
  inp.min       = 12
  inp.max       = 90
  inp.style.cssText = FIELD_STYLE + ';max-width:80px'
  return inp
}

function buildSelect(options, currentValue) {
  const sel = document.createElement('select')
  sel.style.cssText = FIELD_STYLE + ';max-width:220px;cursor:pointer'
  options.forEach(([value, label]) => {
    const opt = document.createElement('option')
    opt.value       = value
    opt.textContent = label
    opt.selected    = value === currentValue
    sel.appendChild(opt)
  })
  return sel
}

function readValue(key, control) {
  if (key === 'fitzpatrick') {
    const val = control.value
    if (!val) return { apiValue: null, displayText: null }
    return { apiValue: val, displayText: `Tipo ${val}` }
  }
  if (key === 'skin_type') {
    const val = control.value
    if (!val) return { apiValue: null, displayText: null }
    return { apiValue: val, displayText: capitalize(val) }
  }
  if (key === 'allergies') {
    const arr = control.value.split(',').map(s => s.trim()).filter(Boolean)
    return { apiValue: arr, displayText: arr.length ? arr.join(', ') : 'Ninguna' }
  }
  // age
  const val = parseInt(control.value)
  if (!val || val < 12 || val > 90) return { apiValue: null, displayText: null }
  return { apiValue: val, displayText: `${val} años` }
}

// ── Change Password Modal ─────────────────────────────────────────────────

const EYE_OPEN  = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
const EYE_CLOSE = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`

window.openChangePasswordModal = function () {
  const existing = document.getElementById('change-pw-modal')
  if (existing) existing.remove()

  const overlay = document.createElement('div')
  overlay.id = 'change-pw-modal'
  overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;z-index:9999;padding:16px'

  overlay.innerHTML = `
    <div role="dialog" aria-modal="true" aria-labelledby="cpw-title"
      style="background:#fff;border-radius:16px;padding:28px 24px;max-width:400px;width:100%;box-shadow:0 8px 32px rgba(0,0,0,0.12)">

      <h2 id="cpw-title" style="font-family:'Fraunces',serif;font-size:18px;color:#181C24;margin:0 0 4px">
        Cambiar contraseña
      </h2>
      <p style="font-size:12px;color:#5A6474;margin:0 0 20px;line-height:1.5">
        Elige una nueva contraseña con al menos 8 caracteres, mayúscula, minúscula, número y un carácter especial (ej. guión -).
      </p>

      <div id="cpw-error"   style="display:none;background:#FFF5F5;border:1.5px solid #FED7D7;color:#C53030;font-size:12px;border-radius:8px;padding:10px 12px;margin-bottom:14px"></div>
      <div id="cpw-success" style="display:none;background:#F0FFF4;border:1.5px solid #9AE6B4;color:#276749;font-size:12px;border-radius:8px;padding:10px 12px;margin-bottom:14px"></div>

      ${buildPwField('cpw-current', 'Contraseña actual')}
      ${buildPwField('cpw-new',     'Nueva contraseña')}

      <div id="cpw-strength" style="margin:-8px 0 14px;display:flex;gap:4px;align-items:center">
        <div style="display:flex;gap:3px;flex:1">
          <div id="cpw-bar-1" style="height:3px;flex:1;border-radius:2px;background:#E8E2D6;transition:background .2s"></div>
          <div id="cpw-bar-2" style="height:3px;flex:1;border-radius:2px;background:#E8E2D6;transition:background .2s"></div>
          <div id="cpw-bar-3" style="height:3px;flex:1;border-radius:2px;background:#E8E2D6;transition:background .2s"></div>
        </div>
        <span id="cpw-strength-label" style="font-size:10px;color:#5A6474;min-width:36px;text-align:right"></span>
      </div>

      ${buildPwField('cpw-confirm', 'Confirmar nueva contraseña')}
      <p id="cpw-match-msg" style="display:none;font-size:11px;color:#C53030;margin:-10px 0 14px"></p>

      <button id="btn-cpw-submit"
        style="width:100%;background:#233D30;color:#FAF8F3;border:none;border-radius:999px;padding:12px;font-size:13px;font-weight:600;cursor:pointer;margin-bottom:10px;transition:opacity .15s">
        Actualizar contraseña
      </button>
      <button id="btn-cpw-cancel"
        style="width:100%;background:transparent;border:none;font-size:12px;color:#5A6474;cursor:pointer;padding:6px">
        Cancelar
      </button>
    </div>
  `

  document.body.appendChild(overlay)
  document.getElementById('cpw-current').focus()

  // close on backdrop click
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeChangePwModal() })

  // close on Escape
  overlay._keyHandler = (e) => { if (e.key === 'Escape') closeChangePwModal() }
  document.addEventListener('keydown', overlay._keyHandler)

  document.getElementById('btn-cpw-cancel').onclick = closeChangePwModal

  // strength meter
  const newField = document.getElementById('cpw-new')
  newField.addEventListener('input', () => updateStrength(newField.value))

  // match check on confirm
  const confirmField = document.getElementById('cpw-confirm')
  confirmField.addEventListener('input', () => checkMatch(newField.value, confirmField.value))

  // submit
  document.getElementById('btn-cpw-submit').onclick = submitChangePassword
}

function buildPwField(id, label) {
  return `
    <div style="margin-bottom:14px">
      <label for="${id}" style="font-size:11px;font-weight:500;color:#5A6474;display:block;margin-bottom:4px">${label}</label>
      <div style="position:relative">
        <input id="${id}" type="password" autocomplete="off"
          style="width:100%;border:1.5px solid #E8E2D6;border-radius:10px;padding:10px 38px 10px 12px;font-size:13px;box-sizing:border-box;outline:none;font-family:inherit;color:#181C24;background:#fff;transition:border-color .15s"
          onfocus="this.style.borderColor='#B89A72'" onblur="this.style.borderColor='#E8E2D6'" />
        <button type="button" tabindex="-1"
          onclick="window._togglePwVisibility('${id}', this)"
          aria-label="Mostrar/ocultar contraseña"
          style="position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:#5A6474;padding:2px;display:flex;align-items:center">
          ${EYE_OPEN}
        </button>
      </div>
    </div>
  `
}

window._togglePwVisibility = function (inputId, btn) {
  const inp = document.getElementById(inputId)
  const isHidden = inp.type === 'password'
  inp.type = isHidden ? 'text' : 'password'
  btn.innerHTML = isHidden ? EYE_CLOSE : EYE_OPEN
}

function pwRequirements(pw) {
  return {
    length:  pw.length >= 8,
    upper:   /[A-Z]/.test(pw),
    lower:   /[a-z]/.test(pw),
    digit:   /[0-9]/.test(pw),
    special: /[^A-Za-z0-9]/.test(pw),
  }
}

function updateStrength(pw) {
  const bars  = [1, 2, 3].map(n => document.getElementById(`cpw-bar-${n}`))
  const label = document.getElementById('cpw-strength-label')
  if (!bars[0] || !label) return

  if (pw.length === 0) {
    bars.forEach(b => { b.style.background = '#E8E2D6' })
    label.textContent = ''
    label.style.color = '#5A6474'
    return
  }

  const r   = pwRequirements(pw)
  const met = [r.length, r.upper && r.lower, r.digit, r.special].filter(Boolean).length

  let barColors, labelText, labelColor
  if (met <= 1) {
    barColors  = ['#FC8181', '#E8E2D6', '#E8E2D6']
    labelText  = 'Débil'
    labelColor = '#C53030'
  } else if (met <= 3) {
    barColors  = ['#F6AD55', '#F6AD55', '#E8E2D6']
    labelText  = 'Media'
    labelColor = '#C05621'
  } else {
    barColors  = ['#68D391', '#68D391', '#68D391']
    labelText  = 'Fuerte'
    labelColor = '#276749'
  }

  bars.forEach((b, i) => { b.style.background = barColors[i] })
  label.textContent = labelText
  label.style.color = labelColor
}

function checkMatch(pw, confirm) {
  const msg = document.getElementById('cpw-match-msg')
  if (!msg) return
  if (confirm.length === 0) { msg.style.display = 'none'; return }
  if (pw !== confirm) {
    msg.textContent    = 'Las contraseñas no coinciden.'
    msg.style.display  = 'block'
  } else {
    msg.style.display = 'none'
  }
}

function closeChangePwModal() {
  const overlay = document.getElementById('change-pw-modal')
  if (!overlay) return
  document.removeEventListener('keydown', overlay._keyHandler)
  overlay.remove()
}

async function submitChangePassword() {
  const currentPw = document.getElementById('cpw-current')?.value ?? ''
  const newPw     = document.getElementById('cpw-new')?.value ?? ''
  const confirm   = document.getElementById('cpw-confirm')?.value ?? ''
  const errorBox  = document.getElementById('cpw-error')
  const successBox = document.getElementById('cpw-success')
  const submitBtn  = document.getElementById('btn-cpw-submit')

  const showErr = (msg) => {
    errorBox.textContent    = msg
    errorBox.style.display  = 'block'
    successBox.style.display = 'none'
  }
  errorBox.style.display   = 'none'
  successBox.style.display = 'none'

  if (!currentPw) return showErr('Ingresa tu contraseña actual.')
  const r = pwRequirements(newPw)
  if (!r.length)  return showErr('La contraseña debe tener al menos 8 caracteres.')
  if (!r.upper || !r.lower) return showErr('La contraseña debe incluir mayúsculas y minúsculas.')
  if (!r.digit)   return showErr('La contraseña debe incluir al menos un número.')
  if (!r.special) return showErr('La contraseña debe incluir al menos un carácter especial (ej. guión -).')
  if (newPw !== confirm) return showErr('Las contraseñas nuevas no coinciden.')
  if (newPw === currentPw) return showErr('La nueva contraseña debe ser diferente a la actual.')

  submitBtn.disabled    = true
  submitBtn.textContent = 'Actualizando...'
  submitBtn.style.opacity = '0.7'

  try {
    const token = localStorage.getItem('cutislab_token')
    const res   = await fetch(`${API}/users/me/change-password`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body:    JSON.stringify({ current_password: currentPw, new_password: newPw }),
    })
    const data = await res.json()
    if (res.status === 401) throw new Error('Tu sesión ha expirado. Vuelve a iniciar sesión.')
    if (!res.ok) throw new Error(data.detail || 'No se pudo actualizar la contraseña.')

    successBox.textContent   = '¡Contraseña actualizada correctamente!'
    successBox.style.display = 'block'
    submitBtn.textContent    = 'Listo'
    ;['cpw-current', 'cpw-new', 'cpw-confirm'].forEach(id => {
      const el = document.getElementById(id)
      if (el) el.value = ''
    })
    updateStrength('')
    setTimeout(closeChangePwModal, 1800)

  } catch (err) {
    showErr(err.message)
    submitBtn.textContent   = 'Actualizar contraseña'
    submitBtn.disabled      = false
    submitBtn.style.opacity = '1'
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────
function setEl(id, text) {
  const el = document.getElementById(id)
  if (el) el.textContent = text || '--'
}

function getInitials(name) {
  if (!name) return '--'
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase()
}

function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}
