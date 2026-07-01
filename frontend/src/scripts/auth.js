/**
 * auth.js
 * Lógica de formularios: registro, login, recuperar contraseña.
 * Conectado a la API real en /api/auth/.
 */

const API = '/api'

// ── REGISTRO ─────────────────────────────────────────────────────────────
export function initRegister() {
  const form = document.getElementById('form-register')
  if (!form) return

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const btn      = document.getElementById('btn-register')
    const errorBox = document.getElementById('register-error')

    const name    = document.getElementById('reg-name').value.trim()
    const email   = document.getElementById('reg-email').value.trim()
    const pw      = document.getElementById('reg-pw').value
    const pw2     = document.getElementById('reg-pw2').value
    const consent = document.getElementById('reg-consent').checked

    if (!name || !email || !pw || !pw2) return showError(errorBox, 'Completa todos los campos.')
    if (pw.length < 8)  return showError(errorBox, 'La contraseña debe tener al menos 8 caracteres.')
    if (pw !== pw2)     return showError(errorBox, 'Las contraseñas no coinciden.')
    if (!consent)       return showError(errorBox, 'Debes aceptar los términos para continuar.')

    setLoading(btn, true)
    hideError(errorBox)

    try {
      const res  = await fetch(`${API}/auth/register`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ full_name: name, email, password: pw, gdpr_accepted: consent }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error al registrarse.')

      localStorage.setItem('cutislab_token', data.access_token)
      localStorage.setItem('cutislab_user',  JSON.stringify(data.user))
      window._goFull('profile')

    } catch (err) {
      showError(errorBox, err.message)
    } finally {
      setLoading(btn, false)
    }
  })
}

// ── LOGIN ─────────────────────────────────────────────────────────────────
export function initLogin() {
  const form = document.getElementById('form-login')
  if (!form) return

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const btn      = document.getElementById('btn-login')
    const errorBox = document.getElementById('login-error')

    const email = document.getElementById('login-email').value.trim()
    const pw    = document.getElementById('login-pw').value

    if (!email || !pw) return showError(errorBox, 'Completa todos los campos.')

    setLoading(btn, true)
    hideError(errorBox)

    try {
      const res  = await fetch(`${API}/auth/login`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email, password: pw }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Correo o contraseña incorrectos.')

      localStorage.setItem('cutislab_token', data.access_token)
      localStorage.setItem('cutislab_user',  JSON.stringify(data.user))

      // El campo has_profile viene directo del login — sin petición extra
      if (data.user.has_profile) {
        localStorage.setItem('cutislab_profile_complete', '1')
        window._goFull('dashboard')
      } else {
        localStorage.removeItem('cutislab_profile_complete')
        window._goFull('profile')
      }

    } catch (err) {
      showError(errorBox, err.message)
    } finally {
      setLoading(btn, false)
    }
  })
}

// ── RECUPERAR CONTRASEÑA ──────────────────────────────────────────────────
export function initForgotPassword() {
  const btn = document.getElementById('btn-forgot')
  if (!btn) return

  btn.addEventListener('click', () => {
    const email = document.getElementById('login-email').value.trim()
    showForgotModal(email)
  })
}

function showForgotModal(prefillEmail) {
  const existing = document.getElementById('forgot-modal')
  if (existing) existing.remove()

  const modal = document.createElement('div')
  modal.id = 'forgot-modal'
  modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:9999;padding:16px'
  modal.innerHTML = `
    <div style="background:#fff;border-radius:14px;padding:28px;max-width:380px;width:100%">
      <h2 style="font-family:'Fraunces',serif;font-size:18px;color:#181C24;margin-bottom:6px">Restablecer contraseña</h2>
      <p style="font-size:12px;color:#5A6474;margin-bottom:18px;line-height:1.5">Ingresa tu correo y te enviaremos un enlace para crear una nueva contraseña.</p>

      <div id="forgot-error"   style="display:none;background:#FFF5F5;border:1px solid #FED7D7;color:#C53030;font-size:12px;border-radius:8px;padding:10px 12px;margin-bottom:12px"></div>
      <div id="forgot-success" style="display:none;background:#F0FFF4;border:1px solid #9AE6B4;color:#276749;font-size:12px;border-radius:8px;padding:10px 12px;margin-bottom:12px"></div>

      <label style="font-size:11px;font-weight:500;color:#5A6474;display:block;margin-bottom:4px">Correo electrónico</label>
      <input id="forgot-email" type="email" value="${prefillEmail}"
        style="width:100%;border:1.5px solid #E8E2D6;border-radius:10px;padding:10px 12px;font-size:13px;margin-bottom:16px;box-sizing:border-box;outline:none;font-family:inherit"
        placeholder="tu@email.com" />

      <button id="btn-send-reset" onclick="sendResetEmail()"
        style="width:100%;background:#233D30;color:#FAF8F3;border:none;border-radius:999px;padding:11px;font-size:13px;font-weight:600;cursor:pointer;margin-bottom:10px">
        Enviar enlace
      </button>
      <button onclick="document.getElementById('forgot-modal').remove()"
        style="width:100%;background:transparent;border:none;font-size:12px;color:#5A6474;cursor:pointer;padding:6px">
        Cancelar
      </button>
    </div>
  `
  document.body.appendChild(modal)
  document.getElementById('forgot-email').focus()
}

window.sendResetEmail = async function () {
  const email      = document.getElementById('forgot-email').value.trim()
  const errorBox   = document.getElementById('forgot-error')
  const successBox = document.getElementById('forgot-success')
  const btn        = document.getElementById('btn-send-reset')

  if (!email) {
    errorBox.textContent  = 'Ingresa tu correo electrónico.'
    errorBox.style.display = 'block'
    successBox.style.display = 'none'
    return
  }

  btn.textContent = 'Enviando...'
  btn.disabled    = true
  errorBox.style.display = 'none'

  try {
    const res = await fetch(`${API}/auth/forgot-password`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'No se pudo enviar el correo.')

    successBox.textContent   = data.message
    successBox.style.display = 'block'
    btn.textContent = 'Enviado'

  } catch (err) {
    errorBox.textContent   = err.message
    errorBox.style.display = 'block'
    btn.textContent = 'Enviar enlace'
    btn.disabled    = false
  }
}

// ── RESTABLECER CONTRASEÑA (desde enlace de email) ────────────────────────
export function initResetPassword() {
  const form = document.getElementById('form-reset-password')
  if (!form) return

  const token = new URLSearchParams(window.location.search).get('reset_token')
  if (!token) {
    const err = document.getElementById('reset-error')
    if (err) {
      err.textContent = 'Enlace inválido. Solicita un nuevo enlace de restablecimiento.'
      err.classList.remove('hidden')
    }
    return
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const btn        = document.getElementById('btn-reset-submit')
    const errorBox   = document.getElementById('reset-error')
    const successBox = document.getElementById('reset-success')

    const pw  = document.getElementById('reset-pw').value
    const pw2 = document.getElementById('reset-pw2').value

    errorBox.classList.add('hidden')
    successBox.classList.add('hidden')

    if (pw.length < 8)  { errorBox.textContent = 'La contraseña debe tener al menos 8 caracteres.'; errorBox.classList.remove('hidden'); return }
    if (pw !== pw2)     { errorBox.textContent = 'Las contraseñas no coinciden.'; errorBox.classList.remove('hidden'); return }

    btn.disabled    = true
    btn.textContent = 'Guardando...'

    try {
      const res  = await fetch(`${API}/auth/reset-password`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ token, new_password: pw }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'No se pudo restablecer la contraseña.')

      successBox.textContent = data.message
      successBox.classList.remove('hidden')
      form.style.display = 'none'

      // Limpiar el token de la URL sin recargar
      const cleanUrl = window.location.pathname
      window.history.replaceState({}, '', cleanUrl)

      setTimeout(() => window._goFull('auth'), 2500)

    } catch (err) {
      errorBox.textContent = err.message
      errorBox.classList.remove('hidden')
      btn.disabled    = false
      btn.textContent = 'Guardar contraseña'
    }
  })
}

// ── PASSWORD TOGGLE ───────────────────────────────────────────────────────
const EYE_OPEN = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="17" height="17"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>`
const EYE_OFF  = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" width="17" height="17"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" /></svg>`

window.togglePw = function (inputId, btn) {
  const input = document.getElementById(inputId)
  if (!input) return
  const visible = input.type === 'text'
  input.type = visible ? 'password' : 'text'
  btn.innerHTML = visible ? EYE_OPEN : EYE_OFF
  btn.setAttribute('aria-label', visible ? 'Mostrar contraseña' : 'Ocultar contraseña')
}

// ── HELPERS ───────────────────────────────────────────────────────────────
function showError(box, msg) {
  box.textContent = msg
  box.classList.remove('hidden')
}

function hideError(box) {
  box.textContent = ''
  box.classList.add('hidden')
}

function setLoading(btn, loading) {
  btn.disabled = loading
  if (loading && !btn.dataset.originalText) btn.dataset.originalText = btn.textContent
  btn.textContent = loading ? 'Procesando...' : (btn.dataset.originalText || btn.textContent)
}
