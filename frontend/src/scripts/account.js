/**
 * account.js
 * Carga y edición de los datos de cuenta del usuario.
 * Conectado a GET /api/users/me, GET /api/users/profile y PUT /api/users/me.
 */

const API = 'http://localhost:8000/api'

export function initAccount() {
  loadUserData()
  bindDeleteAccount()
}

function bindDeleteAccount() {
  const btn = document.getElementById('btn-delete-account')
  if (!btn) return

  btn.addEventListener('click', async () => {
    if (!confirm('¿Estás seguro? Esta acción no se puede deshacer.')) return

    btn.disabled = true
    btn.textContent = 'Eliminando...'

    const token = localStorage.getItem('skinai_token')
    try {
      const res = await fetch(`${API}/users/me`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Error ${res.status}`)
      }

      // Limpiar todo el estado local y redirigir a login
      localStorage.clear()
      window.location.reload()

    } catch (err) {
      alert('Error al eliminar la cuenta: ' + err.message)
      btn.disabled = false
      btn.textContent = 'Eliminar cuenta'
    }
  })
}

async function loadUserData() {
  const token = localStorage.getItem('skinai_token')

  // Datos básicos del usuario (nombre, email) — vienen del login en localStorage
  const user = JSON.parse(localStorage.getItem('skinai_user') || '{}')

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
      localStorage.setItem('skinai_user', JSON.stringify(user))

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

function initEditFields() {
  // El email no es editable (requeriría verificación por correo)
  const editableFields = [
    { id: 'account-age',       type: 'number', key: 'age'         },
    { id: 'account-fitz',      type: 'text',   key: 'fitzpatrick' },
    { id: 'account-skintype',  type: 'text',   key: 'skin_type'   },
    { id: 'account-allergies', type: 'text',   key: 'allergies'   },
  ]

  editableFields.forEach(({ id, type, key }) => {
    const cell = document.getElementById(id)
    if (!cell) return

    const editBtn = document.createElement('button')
    editBtn.textContent = 'Editar'
    editBtn.style.cssText = 'margin-left:8px;font-size:10px;color:#B89A72;background:none;border:none;cursor:pointer;text-decoration:underline'
    editBtn.onclick = () => startEdit(cell, editBtn, key, type)
    cell.parentElement.appendChild(editBtn)
  })
}

async function startEdit(cell, btn, key, type) {
  const currentText = cell.textContent.replace(' años', '').trim()

  const input = document.createElement('input')
  input.type  = type
  input.value = currentText === '--' ? '' : currentText
  input.style.cssText = 'border:1.5px solid #E8E2D6;border-radius:8px;padding:4px 8px;font-size:12px;outline:none;font-family:inherit;max-width:160px'

  if (key === 'allergies') {
    input.placeholder = 'Ej: retinol, parfum'
  }

  const saveBtn   = document.createElement('button')
  saveBtn.textContent = 'Guardar'
  saveBtn.style.cssText = 'margin-left:6px;font-size:10px;color:#233D30;background:none;border:none;cursor:pointer;font-weight:600'

  const cancelBtn = document.createElement('button')
  cancelBtn.textContent = 'Cancelar'
  cancelBtn.style.cssText = 'margin-left:4px;font-size:10px;color:#5A6474;background:none;border:none;cursor:pointer'

  cell.style.display = 'none'
  btn.style.display  = 'none'
  cell.parentElement.appendChild(input)
  cell.parentElement.appendChild(saveBtn)
  cell.parentElement.appendChild(cancelBtn)
  input.focus()

  cancelBtn.onclick = () => {
    input.remove(); saveBtn.remove(); cancelBtn.remove()
    cell.style.display = ''; btn.style.display = ''
  }

  saveBtn.onclick = async () => {
    const rawValue = input.value.trim()
    if (!rawValue) return

    // Convertir allergies de string a array
    let apiValue = rawValue
    if (key === 'allergies') {
      apiValue = rawValue.split(',').map(s => s.trim()).filter(Boolean)
    } else if (key === 'age') {
      apiValue = parseInt(rawValue)
    }

    try {
      const token = localStorage.getItem('skinai_token')
      const res   = await fetch(`${API}/users/me`, {
        method:  'PUT',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ [key]: apiValue }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Error al guardar.')
      }

      // Actualizar localStorage
      const user = JSON.parse(localStorage.getItem('skinai_user') || '{}')
      user[key] = apiValue
      localStorage.setItem('skinai_user', JSON.stringify(user))

      // Actualizar texto en pantalla
      if (key === 'age') {
        cell.textContent = `${rawValue} años`
      } else if (key === 'allergies') {
        cell.textContent = Array.isArray(apiValue) && apiValue.length ? apiValue.join(', ') : 'Ninguna'
      } else {
        cell.textContent = rawValue
      }

    } catch (err) {
      console.error('Error al guardar:', err.message)
      alert(err.message)
    } finally {
      input.remove(); saveBtn.remove(); cancelBtn.remove()
      cell.style.display = ''; btn.style.display = ''
    }
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
