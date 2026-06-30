/**
 * capture.js
 * Lógica de la página de captura: upload de imagen a POST /api/analysis/upload.
 * Al completar el upload, guarda el analysis_id en sessionStorage y navega a "analyzing".
 *
 * "Tomar foto" abre un modal de verificación facial con MediaPipe (detección en tiempo real).
 * Cuando el rostro permanece centrado durante HOLD_MS ms, captura automáticamente la imagen
 * y permite al usuario confirmarla antes de subirla.
 */

const API = 'http://localhost:8000/api'

export function initCapture() {
  _wireUploadButton()
  _wireCameraButton()
  _wireFaceIdModalButtons()
}

// ── BOTONES PRINCIPALES ──────────────────────────────────────────────────────

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
  const btn = document.getElementById('btn-camera-photo')
  if (!btn) return
  btn.addEventListener('click', () => _openFaceIdModal())
}

// ── FACEID MODAL ─────────────────────────────────────────────────────────────

const OVAL_W_RATIO = 0.64
const OVAL_H_RATIO = 0.82
const HOLD_MS      = 2000
const MODEL_URL    =
  'https://storage.googleapis.com/mediapipe-models/face_detector/' +
  'blaze_face_short_range/float16/1/blaze_face_short_range.tflite'

let _faceDetector    = null
let _mediapipeImport = null
let _stream          = null
let _rafId           = null
let _holdStart       = null
let _didCapture      = false
let _lastTs          = -1

function _fid(id) { return document.getElementById(id) }

function _fidShowOnly(id) {
  ['faceid-loadingState', 'faceid-cameraState', 'faceid-resultState'].forEach(s => {
    const el = _fid(s)
    if (!el) return
    if (s === id) {
      el.classList.remove('hidden')
      el.classList.add('flex')
    } else {
      el.classList.add('hidden')
      el.classList.remove('flex')
    }
  })
}

async function _fidLoadDetector() {
  _fid('faceid-loadingMsg').textContent = 'Descargando detector…'
  if (!_mediapipeImport) {
    _mediapipeImport = import('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs')
  }
  const { FaceDetector, FilesetResolver } = await _mediapipeImport
  _fid('faceid-loadingMsg').textContent = 'Cargando modelo…'
  _faceDetector = await FaceDetector.createFromOptions(
    await FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm'
    ),
    {
      baseOptions: { modelAssetPath: MODEL_URL, delegate: 'GPU' },
      runningMode: 'VIDEO',
      minDetectionConfidence: 0.5,
      minSuppressionThreshold: 0.3
    }
  )
}

async function _fidStartCamera() {
  _stream = await navigator.mediaDevices.getUserMedia({
    video: {
      facingMode: 'user',
      aspectRatio: { ideal: 0.75 },
      width:  { ideal: 720 },
      height: { ideal: 960 }
    },
    audio: false
  })
  const video = _fid('faceid-video')
  video.srcObject = _stream
  await new Promise(res => video.addEventListener('loadedmetadata', res, { once: true }))
  video.play()
  const overlay  = _fid('faceid-overlay')
  overlay.width  = video.videoWidth
  overlay.height = video.videoHeight
}

function _fidStopCamera() {
  if (_rafId)  { cancelAnimationFrame(_rafId); _rafId = null }
  if (_stream) { _stream.getTracks().forEach(t => t.stop()); _stream = null }
}

function _fidDetectLoop(ts) {
  if (_didCapture) return
  const video = _fid('faceid-video')
  if (video && video.readyState >= 2 && ts !== _lastTs) {
    _lastTs = ts
    const result = _faceDetector.detectForVideo(video, ts)
    _fidProcessFrame(result.detections)
  }
  _rafId = requestAnimationFrame(_fidDetectLoop)
}

function _fidProcessFrame(detections) {
  const overlay = _fid('faceid-overlay')
  if (!overlay) return
  const W  = overlay.width
  const H  = overlay.height
  const rx = W * OVAL_W_RATIO / 2
  const ry = H * OVAL_H_RATIO / 2
  const cx = W / 2
  const cy = H / 2

  const face = detections
    .filter(d => d.boundingBox)
    .sort((a, b) =>
      b.boundingBox.width * b.boundingBox.height -
      a.boundingBox.width * a.boundingBox.height
    )[0]

  const faceState = face ? _fidGetFaceState(face.boundingBox, cx, cy, rx, ry, W) : 'none'
  const inOval    = faceState === 'ok'
  const now       = performance.now()

  if (inOval) {
    if (!_holdStart) _holdStart = now
    const elapsed = now - _holdStart
    const pct     = Math.min(elapsed / HOLD_MS * 100, 100)
    _fidSetProgress(pct)
    if (elapsed >= HOLD_MS) { _fidTriggerCapture(); return }
    _fidSetStatus('Mantén la posición…', 'text-emerald-400', '#22c55e')
  } else {
    _holdStart = null
    _fidSetProgress(0, false)
    if      (faceState === 'too_small')  _fidSetStatus('Acércate más a la cámara',      'text-blue-400',   '#60a5fa')
    else if (faceState === 'off_center') _fidSetStatus('Centra tu cara en el óvalo',    'text-yellow-400', '#facc15')
    else                                 _fidSetStatus('Posiciona tu cara en el óvalo', 'text-gray-300',   '#9ca3af')
  }

  const ctx = overlay.getContext('2d')
  _fidRenderOverlay(ctx, W, H, cx, cy, rx, ry, inOval, _holdStart ? (now - _holdStart) / HOLD_MS : 0)
}

function _fidGetFaceState(bbox, cx, cy, rx, ry, W) {
  const faceCx    = W - (bbox.originX + bbox.width  / 2)
  const faceCy    =      bbox.originY + bbox.height / 2
  const bigEnough = bbox.width >= rx * 1.40
  const innerRx   = rx * 0.72
  const innerRy   = ry * 0.72
  const dx        = (faceCx - cx) / innerRx
  const dy        = (faceCy - cy) / innerRy
  const centered  = dx * dx + dy * dy <= 1
  if (!bigEnough) return 'too_small'
  if (!centered)  return 'off_center'
  return 'ok'
}

function _fidRenderOverlay(ctx, W, H, cx, cy, rx, ry, inOval, progress) {
  ctx.clearRect(0, 0, W, H)

  ctx.save()
  ctx.fillStyle = 'rgba(0,0,0,0.52)'
  ctx.beginPath()
  ctx.rect(0, 0, W, H)
  ctx.ellipse(cx, cy, rx + 4, ry + 4, 0, 0, Math.PI * 2)
  ctx.fill('evenodd')
  ctx.restore()

  const t       = performance.now() / 1000
  const dashLen = Math.max(8,  W * 0.025)
  const gapLen  = Math.max(6,  W * 0.018)
  const lw      = Math.max(2.5, W * 0.007)
  ctx.save()
  ctx.lineWidth      = lw
  ctx.setLineDash([dashLen, gapLen])
  ctx.lineDashOffset = -t * 18
  ctx.strokeStyle    = inOval ? '#22c55e' : 'rgba(255,255,255,0.85)'
  ctx.shadowColor    = inOval ? '#22c55e' : 'transparent'
  ctx.shadowBlur     = inOval ? 14 : 0
  ctx.beginPath()
  ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2)
  ctx.stroke()
  ctx.restore()

  if (progress > 0.01) {
    const start = -Math.PI / 2
    const end   = start + progress * Math.PI * 2
    ctx.save()
    ctx.lineWidth   = Math.max(3.5, W * 0.009)
    ctx.setLineDash([])
    ctx.strokeStyle = '#22c55e'
    ctx.lineCap     = 'round'
    ctx.shadowColor = '#22c55e'
    ctx.shadowBlur  = 10
    ctx.beginPath()
    ctx.ellipse(cx, cy, rx, ry, 0, start, end)
    ctx.stroke()
    ctx.restore()
  }

  if (!inOval) _fidDrawCornerAccents(ctx, cx, cy, rx, ry)
}

function _fidDrawCornerAccents(ctx, cx, cy, rx, ry) {
  const corners = [-0.18, -0.82, 0.18, 0.82].map(f => f * Math.PI)
  const arcSpan = 0.22
  ctx.save()
  ctx.strokeStyle = 'rgba(255,255,255,0.22)'
  ctx.lineWidth   = 2
  ctx.setLineDash([])
  for (const a of corners) {
    ctx.beginPath()
    ctx.ellipse(cx, cy, rx, ry, 0, a - arcSpan / 2, a + arcSpan / 2)
    ctx.stroke()
  }
  ctx.restore()
}

function _fidTriggerCapture() {
  _didCapture = true
  cancelAnimationFrame(_rafId)
  _rafId = null

  const flash = _fid('faceid-flash')
  if (flash) { flash.classList.add('active'); setTimeout(() => flash.classList.remove('active'), 180) }

  const video  = _fid('faceid-video')
  const cap    = document.createElement('canvas')
  cap.width    = video.videoWidth
  cap.height   = video.videoHeight
  const capCtx = cap.getContext('2d')
  capCtx.save()
  capCtx.scale(-1, 1)
  capCtx.drawImage(video, -cap.width, 0)
  capCtx.restore()
  const dataURL = cap.toDataURL('image/jpeg', 0.93)

  setTimeout(() => {
    _fidStopCamera()
    const img = _fid('faceid-capturedPhoto')
    const btn = _fid('faceid-usePhotoBtn')
    if (img) img.src = dataURL
    if (btn) btn.dataset.photoUrl = dataURL
    _fidShowOnly('faceid-resultState')
  }, 280)
}

function _fidSetStatus(text, colorClass, dotColor) {
  const msg = _fid('faceid-statusMsg')
  const dot = _fid('faceid-statusDot')
  if (msg) { msg.textContent = text; msg.className = `text-sm font-medium transition-colors duration-300 ${colorClass}` }
  if (dot) dot.style.background = dotColor
}

function _fidSetProgress(pct, visible = true) {
  const wrap = _fid('faceid-progressWrap')
  const fill = _fid('faceid-progressFill')
  if (wrap) wrap.style.visibility = (visible && pct > 0) ? 'visible' : 'hidden'
  if (fill) fill.style.width      = `${pct}%`
}

function _fidResetCamera() {
  _fidStopCamera()
  _didCapture = false
  _holdStart  = null
  _lastTs     = -1
  _fidSetProgress(0, false)
}

async function _openFaceIdModal() {
  const modal = _fid('faceid-modal')
  if (!modal) return
  modal.classList.remove('hidden')
  modal.classList.add('flex')
  _fidShowOnly('faceid-loadingState')

  try {
    if (!_faceDetector) await _fidLoadDetector()
    _fid('faceid-loadingMsg').textContent = 'Abriendo cámara…'
    await _fidStartCamera()
    _fidShowOnly('faceid-cameraState')
    _fidSetStatus('Posiciona tu cara en el óvalo', 'text-gray-300', '#9ca3af')
    _didCapture = false
    _holdStart  = null
    _lastTs     = -1
    _rafId = requestAnimationFrame(_fidDetectLoop)
  } catch (err) {
    console.error(err)
    const msg = err.name === 'NotAllowedError'
      ? 'Permiso de cámara denegado. Revisa la configuración del navegador.'
      : `No se pudo iniciar la cámara: ${err.message}`
    _fidResetCamera()
    _closeFaceIdModal()
    _showError(msg)
  }
}

function _closeFaceIdModal() {
  _fidResetCamera()
  const modal = _fid('faceid-modal')
  if (modal) { modal.classList.add('hidden'); modal.classList.remove('flex') }
}

function _wireFaceIdModalButtons() {
  const cancelLoadBtn = _fid('faceid-cancelLoadBtn')
  const cancelBtn     = _fid('faceid-cancelBtn')
  const retakeBtn     = _fid('faceid-retakeBtn')
  const usePhotoBtn   = _fid('faceid-usePhotoBtn')

  if (cancelLoadBtn) cancelLoadBtn.addEventListener('click', () => _closeFaceIdModal())
  if (cancelBtn)     cancelBtn.addEventListener('click',     () => _closeFaceIdModal())

  if (retakeBtn) retakeBtn.addEventListener('click', async () => {
    _fidResetCamera()
    _fidShowOnly('faceid-loadingState')
    _fid('faceid-loadingMsg').textContent = 'Abriendo cámara…'
    try {
      await _fidStartCamera()
      _fidShowOnly('faceid-cameraState')
      _fidSetStatus('Posiciona tu cara en el óvalo', 'text-gray-300', '#9ca3af')
      _didCapture = false
      _holdStart  = null
      _lastTs     = -1
      _rafId = requestAnimationFrame(_fidDetectLoop)
    } catch {
      _closeFaceIdModal()
      _showError('No se pudo acceder a la cámara.')
    }
  })

  if (usePhotoBtn) usePhotoBtn.addEventListener('click', () => {
    const dataURL = usePhotoBtn.dataset.photoUrl || ''
    if (!dataURL) return
    _closeFaceIdModal()
    _uploadFile(_dataURLtoFile(dataURL, 'face-capture.jpg'))
  })
}

function _dataURLtoFile(dataURL, filename) {
  const arr  = dataURL.split(',')
  const mime = arr[0].match(/:(.*?);/)[1]
  const bstr = atob(arr[1])
  let n      = bstr.length
  const u8   = new Uint8Array(n)
  while (n--) u8[n] = bstr.charCodeAt(n)
  return new File([u8], filename, { type: mime })
}

// ── UPLOAD ────────────────────────────────────────────────────────────────────

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
    formData.append('file',     file)
    formData.append('device',   _detectDevice())
    formData.append('lighting', 'unknown')

    const res = await fetch(`${API}/analysis/upload`, {
      method:  'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body:    formData,
    })

    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Error al subir la imagen.')

    sessionStorage.setItem('cutislab_analysis_id', String(data.analysis_id))
    window._goFull('analyzing')

  } catch (err) {
    _setUploadingState(false)
    _showError(err.message)
  }
}

// ── HELPERS ───────────────────────────────────────────────────────────────────

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
