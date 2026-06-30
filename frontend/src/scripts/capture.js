/**
 * capture.js
 * Lógica de la página de captura: upload de imagen a POST /api/analysis/upload.
 * Al completar el upload, guarda el analysis_id en sessionStorage y navega a "analyzing".
 */

const API = 'http://localhost:8000/api'

export function initCapture() {
  _wireUploadButton()
  _wireCameraButton()
}

// ── BOTONES ───────────────────────────────────────────────────────────────

function _wireUploadButton() {
  const btn   = document.getElementById('btn-upload-photo')
  const input = document.getElementById('upload-file-input')
  if (!btn || !input) return

  btn.addEventListener('click', () => input.click())
  input.addEventListener('change', (e) => {
    const file = e.target.files[0]
    if (file) _uploadFile(file)
  })
}

function _wireCameraButton() {
  const btn   = document.getElementById('btn-camera-photo')
  const input = document.getElementById('camera-file-input')
  if (!btn || !input) return

  btn.addEventListener('click', () => input.click())
  input.addEventListener('change', (e) => {
    const file = e.target.files[0]
    if (file) _uploadFile(file)
  })
}

// ── UPLOAD ────────────────────────────────────────────────────────────────

function _detectDevice() {
  const ua = navigator.userAgent
  if (/Mobi|Android/i.test(ua)) return 'mobile'
  if (/Tablet|iPad/i.test(ua))  return 'tablet'
  return 'desktop'
}

async function _uploadFile(file) {
  const token = localStorage.getItem('cutislab_token')
  if (!token) { window._goFull('auth'); return }

  _setUploadingState(true)
  _hideError()

  try {
    const formData = new FormData()
    formData.append('file',    file)
    formData.append('device',  _detectDevice())
    // lighting se puede agregar desde el HTML si hay selector; por ahora 'unknown'
    formData.append('lighting', 'unknown')

    const res = await fetch(`${API}/analysis/upload`, {
      method:  'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body:    formData,
    })

    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Error al subir la imagen.')

    // Guardar analysis_id para que analyzing.js pueda hacer polling
    sessionStorage.setItem('cutislab_analysis_id', String(data.analysis_id))

    // Navegar a la pantalla de análisis en progreso
    window._goFull('analyzing')

  } catch (err) {
    _setUploadingState(false)
    _showError(err.message)
  }
}

// ── HELPERS ───────────────────────────────────────────────────────────────

function _setUploadingState(loading) {
  const btns      = document.getElementById('capture-btns')
  const uploading = document.getElementById('capture-uploading')
  if (btns)      btns.classList.toggle('hidden', loading)
  if (uploading) uploading.classList.toggle('hidden', !loading)
}

function _showError(msg) {
  const box = document.getElementById('capture-upload-error')
  const txt = document.getElementById('capture-upload-error-msg')
  if (txt) txt.textContent = msg
  if (box) box.classList.remove('hidden')
}

function _hideError() {
  const box = document.getElementById('capture-upload-error')
  if (box) box.classList.add('hidden')
}
