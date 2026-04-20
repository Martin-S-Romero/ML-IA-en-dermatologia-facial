/**
 * auth.js
 * Lógica de formularios: registro, login, recuperar contraseña.
 * Conectado a la API real en /api/auth/.
 */

const API = 'http://localhost:8000/api'

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

      localStorage.setItem('skinai_token', data.access_token)
      localStorage.setItem('skinai_user',  JSON.stringify(data.user))
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

      localStorage.setItem('skinai_token', data.access_token)
      localStorage.setItem('skinai_user',  JSON.stringify(data.user))
      window._goFull('dashboard')

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
