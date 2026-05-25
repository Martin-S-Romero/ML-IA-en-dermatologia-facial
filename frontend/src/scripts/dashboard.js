/**
 * dashboard.js
 * Dashboard conectado a la API real.
 * - initDashboard() carga historial + rutina activa en paralelo
 * - Pobla las tabs: Dashboard, Historial, Gráficas y Rutina
 * - openDetail(id) obtiene el análisis completo y renderiza la vista de detalle
 */

const API = 'http://localhost:8000/api'

// Caché de la sesión actual (se reinicia cuando se navega al dashboard)
let _analyses = []
let _routine  = null

// ── INICIALIZACIÓN PRINCIPAL ──────────────────────────────────────────────

export async function initDashboard() {
  const token = localStorage.getItem('skinai_token')
  if (!token) return

  try {
    const [analyses, routine] = await Promise.all([
      _fetchHistory(token),
      _fetchRoutine(token),
    ])
    _analyses = analyses
    _routine  = routine

    _populateDashTab(analyses)
    _populateHistoryTab(analyses)
    _populateRoutineTab(routine)

    // Exponer datos para charts.js (lazy load al entrar a la tab Gráficas)
    window._skinaiAnalyses = analyses
  } catch (err) {
    console.error('[dashboard] Error al cargar datos:', err)
  }
}

// ── FETCH HELPERS ─────────────────────────────────────────────────────────

async function _fetchHistory(token) {
  try {
    const res = await fetch(`${API}/analysis/history?limit=20`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!res.ok) return []
    return res.json()
  } catch { return [] }
}

async function _fetchRoutine(token) {
  try {
    const res = await fetch(`${API}/routines/active`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!res.ok) return null
    return res.json()
  } catch { return null }
}

// ── TAB: DASHBOARD (resumen) ──────────────────────────────────────────────

function _populateDashTab(analyses) {
  const latestEl = document.getElementById('dash-latest')
  if (!latestEl) return

  // Buscar el análisis completado más reciente
  const latest = analyses.find(a => a.status === 'completed') || analyses[0]
  if (!latest) return  // mantener el estado por defecto "Sin análisis aún"

  const dateStr = _formatDate(latest.created_at)

  latestEl.innerHTML = `
    <p class="text-[10px] text-white/55 uppercase tracking-widest mb-3">
      Análisis #${latest.id} · ${dateStr}
    </p>
    <h2 class="font-display text-lg text-cream mb-1">Análisis de piel</h2>
    <p class="text-xs text-white/70 mb-1">Estado: ${_statusLabel(latest.status)}</p>
    <p class="text-[11px] text-white/50 mb-4">
      La clasificación ML de condiciones dérmicas se activará en la Fase 8 del proyecto.
    </p>
    <div class="flex gap-2 flex-wrap">
      <button
        class="bg-bark text-ink text-xs font-semibold py-2 px-4 rounded-full hover:bg-bark/90 transition-colors"
        onclick="dtab('dh')"
      >Ver historial</button>
      <button
        class="bg-white/15 text-white text-xs font-semibold py-2 px-4 rounded-full hover:bg-white/25 transition-colors"
        data-go="capture"
      >Nuevo análisis</button>
    </div>
  `
}

// ── TAB: HISTORIAL ────────────────────────────────────────────────────────

function _populateHistoryTab(analyses) {
  const container = document.getElementById('hist-items')
  if (!container) return

  if (!analyses.length) {
    container.innerHTML = `
      <div class="card card-body text-center py-10">
        <p class="text-xs text-slate">No tienes análisis registrados aún.</p>
        <button class="btn-primary mt-4 max-w-xs mx-auto" data-go="capture">
          Hacer primer análisis
        </button>
      </div>`
    return
  }

  container.innerHTML = analyses.map((a) => {
    const dateStr    = _formatDate(a.created_at)
    const statusLbl  = _statusLabel(a.status)
    const statusCls  = a.status === 'completed' ? 'text-ok'
                     : a.status === 'failed'    ? 'text-rose'
                     :                            'text-warn'

    return `
      <div
        class="card card-body mb-3 cursor-pointer hover:shadow-md transition-shadow"
        onclick="openDetail(${a.id})"
        role="button"
        aria-label="Abrir análisis #${a.id}"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-[10px] font-bold text-forest bg-forest/10 rounded px-2 py-0.5">
            Análisis #${a.id}
          </span>
          <span class="text-[10px] ${statusCls} font-semibold">${statusLbl}</span>
        </div>
        <p class="text-xs font-semibold text-ink mb-0.5">Análisis de piel</p>
        <p class="text-[10px] text-slate">${dateStr}</p>
        <div class="flex justify-end mt-2">
          <span class="text-[10px] text-forest font-semibold">Ver detalle →</span>
        </div>
      </div>`
  }).join('')
}

// ── TAB: RUTINA ───────────────────────────────────────────────────────────

function _populateRoutineTab(routine) {
  const emptyEl = document.getElementById('routine-empty')
  const recEl   = document.getElementById('routine-recommended')
  const curEl   = document.getElementById('routine-current-products')

  if (!routine || !routine.steps?.length) {
    if (emptyEl) emptyEl.classList.remove('hidden')
    if (recEl)   recEl.classList.add('hidden')
    return
  }

  if (emptyEl) emptyEl.classList.add('hidden')
  if (recEl)   recEl.classList.remove('hidden')

  const meta = document.getElementById('routine-recommended-meta')
  if (meta) meta.textContent = `Creada el ${_formatDate(routine.created_at)}`

  const amSteps = routine.steps.filter(s => s.time_of_day === 'am' && s.is_active)
  const pmSteps = routine.steps.filter(s => s.time_of_day === 'pm' && s.is_active)

  const amEl = document.getElementById('routine-am')
  const pmEl = document.getElementById('routine-pm')
  if (amEl) amEl.innerHTML = _renderSteps(amSteps)
  if (pmEl) pmEl.innerHTML = _renderSteps(pmSteps)

  // Grid de productos actuales
  if (curEl) {
    const active = routine.steps.filter(s => s.is_active)
    curEl.innerHTML = active.length
      ? active.map(s => `
          <div class="bg-white rounded-xl p-3">
            <p class="text-[11px] font-semibold text-ink leading-snug mb-0.5">${s.product_name}</p>
            <p class="text-[10px] text-slate">
              ${s.product_category || 'Producto'} · ${s.time_of_day === 'am' ? 'Mañana' : 'Noche'}
            </p>
          </div>`).join('')
      : '<p class="text-xs text-slate col-span-full text-center py-4">Sin productos activos.</p>'
  }
}

function _renderSteps(steps) {
  if (!steps.length) {
    return '<p class="text-xs text-slate text-center py-3">Sin pasos para esta franja.</p>'
  }
  return steps.map(s => `
    <div class="flex items-start gap-2.5 py-2.5 border-b border-sand last:border-0">
      <span class="text-lg flex-shrink-0 mt-0.5">${_categoryIcon(s.product_category)}</span>
      <div class="flex-1 min-w-0">
        <p class="text-[11px] font-semibold text-ink leading-snug">
          ${s.step_order}. ${s.product_name}
        </p>
        ${s.product_category
          ? `<p class="text-[10px] text-slate">${s.product_category}</p>`
          : ''}
        ${s.reason
          ? `<p class="text-[10px] text-slate/70 italic mt-0.5">${s.reason}</p>`
          : ''}
      </div>
    </div>`).join('')
}

// ── DETALLE DE ANÁLISIS ───────────────────────────────────────────────────

export async function openDetail(id) {
  const token  = localStorage.getItem('skinai_token')
  const list   = document.getElementById('hist-list')
  const detail = document.getElementById('hist-detail')
  if (!list || !detail) return

  list.classList.add('hidden')
  detail.classList.remove('hidden')
  detail.innerHTML = `
    <div class="text-center py-10 text-xs text-slate animate-pulse">Cargando análisis...</div>`

  try {
    const res = await fetch(`${API}/analysis/${id}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('No se pudo cargar el análisis.')
    const analysis = await res.json()
    _renderDetail(analysis, detail)
  } catch (err) {
    detail.innerHTML = `
      <button class="btn-back-dark mb-4 text-sm" onclick="closeDetail()">← Volver al historial</button>
      <div class="card card-body text-center py-8 text-xs text-rose">${err.message}</div>`
  }
}

function _renderDetail(a, container) {
  const token = localStorage.getItem('skinai_token')
  const dateStr = _formatDate(a.created_at)

  const statusBadge = a.status === 'completed'
    ? '<span class="bg-ok/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Completado</span>'
    : a.status === 'failed'
    ? '<span class="bg-rose/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Error</span>'
    : '<span class="bg-warn/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Procesando</span>'

  // Imagen: usa el endpoint con token para autenticarse de forma segura
  const imgSection = a.censored_filename || a.original_filename
    ? `<img
         src="${API}/analysis/${a.id}/image?token=${token}"
         alt="Imagen procesada análisis #${a.id}"
         class="w-full h-full object-cover"
         onerror="this.parentElement.innerHTML='<span class=\\'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-7xl opacity-30 select-none\\'></span>'"
       >`
    : '<span class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-7xl opacity-30 select-none"></span>'

  container.innerHTML = `
    <!-- Volver -->
    <button class="btn-back-dark mb-4 text-sm" onclick="closeDetail()">
      ← Volver al historial
    </button>

    <!-- Cabecera -->
    <div class="bg-gradient-diag rounded-card p-4 text-white mb-4">
      <div class="flex items-center justify-between mb-1.5">
        <span class="bg-white/15 rounded-md px-2 py-0.5 text-[11px] font-bold">
          Análisis #${a.id}
        </span>
        ${statusBadge}
      </div>
      <h2 class="font-display text-lg text-cream mb-0.5">Análisis de piel</h2>
      <p class="text-[11px] text-white/55">${dateStr}</p>
    </div>

    <!-- Imagen procesada -->
    <div class="card card-body mb-4">
      <p class="section-label mb-2">Imagen procesada</p>
      <div class="relative h-48 bg-ink rounded-xl overflow-hidden mb-2 flex items-center justify-center">
        ${imgSection}
      </div>
      <p class="text-[10px] text-slate leading-relaxed">
        La imagen fue censurada automáticamente (ojos y boca difuminados) para
        proteger tu privacidad antes de ser procesada.
      </p>
    </div>

    <!-- Resultados ML -->
    <div class="card card-body mb-4">
      <p class="section-label mb-2">Resultados del modelo ML</p>
      <div class="info-box text-[11px]">
        La clasificación automática de condiciones dérmicas (acné, rosácea, manchas)
        estará disponible en la Fase 8 del proyecto cuando el modelo ONNX esté integrado.
        La imagen ya fue procesada y anonimizada correctamente.
      </div>
    </div>

    ${a.error_message ? `
    <div class="bg-[#FFF5F5] border border-rose/30 rounded-card p-3 mb-4">
      <p class="text-[11px] text-rose font-semibold mb-1">Error detectado:</p>
      <p class="text-[11px] text-rose">${a.error_message}</p>
    </div>` : ''}

    <!-- Nueva captura -->
    <button class="btn-primary w-full mt-2" data-go="capture">
      Nuevo análisis
    </button>
  `
}

export function closeDetail() {
  const list   = document.getElementById('hist-list')
  const detail = document.getElementById('hist-detail')
  if (list)   list.classList.remove('hidden')
  if (detail) { detail.classList.add('hidden'); detail.innerHTML = '' }
}

// ── DASHBOARD TABS ────────────────────────────────────────────────────────

const TAB_IDS = ['dd', 'dh', 'dg', 'dr']

export function dtab(name) {
  TAB_IDS.forEach(id => {
    const page = document.getElementById(id)
    const btn  = document.querySelector(`.dtab[data-tab="${id}"]`)
    if (page) page.classList.toggle('active', id === name)
    if (btn)  {
      btn.classList.toggle('active', id === name)
      btn.setAttribute('aria-selected', String(id === name))
    }
  })

  // El botón de Dashboard en el sidebar permanece activo en todas las sub-tabs
  const sidebarDash = document.getElementById('sidebar-dash-btn')
  if (sidebarDash) sidebarDash.classList.add('active')

  if (name === 'dg') {
    import('./charts.js').then(m => m.initCharts())
  }
}

// ── SIDEBAR NAV ───────────────────────────────────────────────────────────

export function sidebarNav(tabId) {
  if (!document.getElementById('page-dashboard')) {
    window._goFull && window._goFull('dashboard')
    setTimeout(() => dtab(tabId), 300)
  } else {
    dtab(tabId)
  }
}

// ── RUTINA — switch AM/PM ─────────────────────────────────────────────────

export function switchRoutine(t) {
  const am   = document.getElementById('routine-am')
  const pm   = document.getElementById('routine-pm')
  const rtAm = document.getElementById('rtab-am')
  const rtPm = document.getElementById('rtab-pm')

  if (am) am.classList.toggle('hidden', t !== 'am')
  if (pm) pm.classList.toggle('hidden', t !== 'pm')

  if (rtAm) {
    rtAm.className = t === 'am'
      ? 'flex-1 py-2 rounded-md text-xs font-semibold bg-warn text-white border-none cursor-pointer transition-all'
      : 'flex-1 py-2 rounded-md text-xs font-semibold bg-cream text-slate border-[1.5px] border-sand cursor-pointer transition-all'
  }
  if (rtPm) {
    rtPm.className = t === 'pm'
      ? 'flex-1 py-2 rounded-md text-xs font-semibold bg-forest text-white border-none cursor-pointer transition-all'
      : 'flex-1 py-2 rounded-md text-xs font-semibold bg-cream text-slate border-[1.5px] border-sand cursor-pointer transition-all'
  }
}

// ── ACORDEÓN ──────────────────────────────────────────────────────────────

export function toggleAccordion(id) {
  const el = document.getElementById(id)
  if (!el) return
  const isOpen = el.classList.contains('open')
  document.querySelectorAll('.accordion-card').forEach(c => c.classList.remove('open'))
  if (!isOpen) el.classList.add('open')
}

// ── HELPERS ───────────────────────────────────────────────────────────────

function _formatDate(isoStr) {
  if (!isoStr) return '--'
  try {
    return new Date(isoStr).toLocaleDateString('es-ES', {
      day: 'numeric', month: 'long', year: 'numeric',
    })
  } catch { return isoStr }
}

function _statusLabel(status) {
  return (
    { completed: 'Completado', failed: 'Error', processing: 'Procesando' }[status]
    || status
  )
}

function _categoryIcon(category) {
  const map = {
    limpiador:  '',
    tónico:     '',
    sérum:      '',
    hidratante: '',
    protector:  '',
    exfoliante: '',
    mascarilla: '',
    contorno:   '',
  }
  return map[(category || '').toLowerCase()] || ''
}
