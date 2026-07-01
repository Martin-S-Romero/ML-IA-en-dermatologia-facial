/**
 * analyzing.js
 * Lógica de la página "Analizando tu piel":
 * - Anima los pasos de forma progresiva
 * - Hace polling a GET /api/analysis/{id}/status cada 2 segundos
 * - Al completar → navega al dashboard
 * - Al fallar    → muestra error y botón de regreso
 */

const API           = '/api'
const POLL_INTERVAL = 2000   // ms entre cada consulta de estado

// Retardo (ms desde el inicio) en que cada paso se activa visualmente.
// null = se activa sólo cuando la API confirma el estado final.
const STEP_TIMINGS = [0, 800, 1600, 2400, 3200, null]

let _pollTimer = null

export function initAnalyzing() {
  const analysisId = sessionStorage.getItem('cutislab_analysis_id')

  if (!analysisId) {
    // Sin ID — redirigir a captura tras un instante
    setTimeout(() => window._goFull && window._goFull('capture'), 1500)
    return
  }

  _startStepAnimations()

  // Iniciar polling con un pequeño delay para que las animaciones arranquen primero
  setTimeout(() => _startPolling(parseInt(analysisId, 10)), 1000)
}

// ── ANIMACIÓN DE PASOS ────────────────────────────────────────────────────

function _startStepAnimations() {
  STEP_TIMINGS.forEach((delay, i) => {
    if (delay === null) return
    setTimeout(() => _activateStep(i + 1), delay)
  })
}

function _activateStep(stepNum) {
  const li = document.querySelector(`[data-step="${stepNum}"]`)
  if (!li) return
  const dot  = li.querySelector('div')
  const span = li.querySelector('span')
  if (dot)  dot.className  = 'w-2 h-2 rounded-full bg-ok flex-shrink-0 transition-all duration-300'
  if (span) span.className = 'text-ink font-medium transition-all duration-300'
}

function _failStep(stepNum) {
  const li = document.querySelector(`[data-step="${stepNum}"]`)
  if (!li) return
  const dot  = li.querySelector('div')
  const span = li.querySelector('span')
  if (dot)  dot.className  = 'w-2 h-2 rounded-full bg-rose flex-shrink-0'
  if (span) span.className = 'text-rose'
}

// ── POLLING ───────────────────────────────────────────────────────────────

function _startPolling(analysisId) {
  const token = localStorage.getItem('cutislab_token')
  if (!token) return

  _pollTimer = setInterval(async () => {
    // Si el usuario navegó a otra página, detener polling
    if (!document.getElementById('page-analyzing')) {
      clearInterval(_pollTimer)
      return
    }

    try {
      const res = await fetch(`${API}/analysis/${analysisId}/status`, {
        headers: { 'Authorization': `Bearer ${token}` },
      })

      // 404 = registro borrado porque no se detectó rostro
      if (res.status === 404) {
        clearInterval(_pollTimer)
        sessionStorage.removeItem('cutislab_analysis_id')
        _failStep(6)
        _showFailedState()
        return
      }
      if (!res.ok) return   // error de red transitorio — reintentar en el próximo tick

      const data = await res.json()

      if (data.status === 'completed') {
        clearInterval(_pollTimer)
        // Activar pasos 6 y 7 con pequeño retraso para dar sensación de finalización
        _activateStep(6)
        setTimeout(() => {
          sessionStorage.removeItem('cutislab_analysis_id')
          window._goFull && window._goFull('dashboard')
        }, 900)

      } else if (data.status === 'failed') {
        clearInterval(_pollTimer)
        _failStep(6)
        _showFailedState()
      }
      // 'processing' → seguir esperando

    } catch (err) {
      // Error de red transitorio — no detener el polling
      console.warn('[analyzing] Polling error (retrying):', err)
    }
  }, POLL_INTERVAL)
}

// ── ESTADO DE ERROR ───────────────────────────────────────────────────────

function _showFailedState() {
  const page = document.getElementById('page-analyzing')
  if (!page) return

  const inner = page.querySelector('.max-w-md')
  if (!inner) return

  // Quitar el anillo de carga
  const ring = inner.querySelector('.analyzing-ring')
  if (ring) ring.remove()

  // Reemplazar título y párrafo intro
  const h1 = inner.querySelector('h1')
  const p  = inner.querySelector('p')
  if (h1) h1.textContent = 'No se pudo analizar'
  if (p)  {
    p.textContent = 'No se detectó un rostro claro en la imagen. Por favor intenta con una foto con buena iluminación y ángulo frontal.'
  }

  // Insertar botón de regreso si no existe ya
  if (!inner.querySelector('#btn-retry-capture')) {
    const btn = document.createElement('button')
    btn.id        = 'btn-retry-capture'
    btn.className = 'btn-primary max-w-xs mt-4'
    btn.textContent = 'Volver a capturar'
    btn.onclick   = () => window._goFull && window._goFull('capture')
    inner.appendChild(btn)
  }
}
