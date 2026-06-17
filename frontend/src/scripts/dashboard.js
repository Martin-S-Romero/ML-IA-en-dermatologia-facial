/**
 * dashboard.js
 * Dashboard conectado a la API real.
 * - initDashboard() carga historial + rutina activa en paralelo
 * - Pobla las tabs: Dashboard, Historial, Gráficas y Rutina
 * - openDetail(id) obtiene el análisis completo y renderiza la vista de detalle
 */

const API = 'http://localhost:8000/api'

// Caché de la sesión actual (se reinicia cuando se navega al dashboard)
let _analyses       = []
let _routine        = null
let _analysisUserNum = {}   // map: db_id → número relativo al usuario

// ── TRADUCCIONES ──────────────────────────────────────────────────────────────

const _LABEL_ES = {
  'acne-comedonal':        'Acné comedonal',
  'acne-excoriated':       'Acné excoriado',
  'acne-inflammatory':     'Acné inflamatorio',
  'perioral-dermatitis':   'Dermatitis perioral',
  'rosacea-etr':           'Rosácea ETR',
  'rosacea-inflammatory':  'Rosácea inflamatoria',
  'seborrheic-dermatitis': 'Dermatitis seborreica',
  'healthy-skin':          'Piel saludable',
}

const _DESCRIPCIONES = {
  'acne-comedonal':        'Acné comedonal — puntos negros/blancos, zona T',
  'acne-excoriated':       'Acné excoriado — marcas de rascado, mejillas/mentón',
  'acne-inflammatory':     'Acné inflamatorio — pústulas/nódulos, cara',
  'perioral-dermatitis':   'Dermatitis perioral — zona alrededor de la boca',
  'rosacea-etr':           'Rosácea eritematotelangiectásica — mejillas simétricas',
  'rosacea-inflammatory':  'Rosácea inflamatoria — centro facial',
  'seborrheic-dermatitis': 'Dermatitis seborreica — cejas, nariz, zona T',
  'healthy-skin':          'Piel sin lesiones detectables',
}

const _MENSAJES_ALERTA = {
  'acne-excoriated': 'Este patrón puede beneficiarse de apoyo profesional para el manejo del hábito de rascado. Consulta a tu médico.',
  'perioral-dermatitis': 'La dermatitis perioral puede agravarse con corticosteroides tópicos. Consulta a un dermatólogo antes de aplicar cualquier tratamiento.',
  'rosacea-inflammatory': 'La rosácea inflamatoria requiere evaluación médica. Evita desencadenantes como calor, alcohol y productos con fragancia.',
  'seborrheic-dermatitis': 'La dermatitis seborreica crónica o severa puede confundirse con psoriasis. Consulta a un dermatólogo si los síntomas persisten o se extienden.',
}

const _ZONE_ES = {
  // Zonas principales (zones_display)
  frente:        'Frente',
  mejilla_izq:   'Mejilla izquierda',
  mejilla_der:   'Mejilla derecha',
  nariz:         'Nariz',
  menton:        'Mentón',
  // Subzonas diagnósticas (zones_diagnostic)
  ceja_izq:      'Ceja izquierda',
  ceja_der:      'Ceja derecha',
  nariz_lat_izq: 'Lat. nasal izq.',
  nariz_lat_der: 'Lat. nasal der.',
  mandibula_izq: 'Mandíbula izq.',
  mandibula_der: 'Mandíbula der.',
  zona_perioral: 'Zona perioral',
}

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

  // El historial ya viene filtrado a completados; el primero es el más reciente
  const latest = analyses[0]
  if (!latest) return  // mantener el estado por defecto "Sin análisis aún"

  const userNum = analyses.length
  const dateStr = _formatDate(latest.created_at)
  const label   = _LABEL_ES[latest.top1_label] || 'Análisis completado'
  const confPct = latest.top1_confidence != null
    ? Math.round(latest.top1_confidence * 100)
    : null

  latestEl.innerHTML = `
    <p class="text-[10px] text-white/55 uppercase tracking-widest mb-3">
      Análisis #${userNum} · ${dateStr}
    </p>
    <h2 class="font-display text-lg text-cream mb-1">${label}</h2>
    ${confPct !== null
      ? `<p class="text-xs text-white/70 mb-4">Confianza: ${confPct}%</p>`
      : `<p class="text-xs text-white/50 mb-4">Estado: ${_statusLabel(latest.status)}</p>`
    }
    <div class="flex gap-2 flex-wrap">
      <button
        class="bg-bark text-ink text-xs font-semibold py-2 px-4 rounded-full hover:bg-bark/90 transition-colors"
        onclick="dtab('dh')"
      >Ver historial</button>
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

  _analysisUserNum = {}
  container.innerHTML = analyses.map((a, i) => {
    const userNum = analyses.length - i   // oldest = #1, newest = #N
    _analysisUserNum[a.id] = userNum
    const dateStr = _formatDate(a.created_at)
    const label   = _LABEL_ES[a.top1_label] || 'Análisis de piel'

    return `
      <div
        class="card card-body mb-3 cursor-pointer hover:shadow-md transition-shadow"
        onclick="openDetail(${a.id})"
        role="button"
        aria-label="Abrir análisis #${userNum}"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-[10px] font-bold text-forest bg-forest/10 rounded px-2 py-0.5">
            Análisis #${userNum}
          </span>
          <span class="text-[10px] text-ok font-semibold">Completado</span>
        </div>
        <p class="text-xs font-semibold text-ink mb-0.5">${label}</p>
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
  const token   = localStorage.getItem('skinai_token')
  const list    = document.getElementById('hist-list')
  const detail  = document.getElementById('hist-detail')
  const userNum = _analysisUserNum[id] || '?'
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
    _renderDetail(analysis, detail, userNum)
  } catch (err) {
    detail.innerHTML = `
      <button class="btn-back-dark mb-4 text-sm" onclick="closeDetail()">← Volver al historial</button>
      <div class="card card-body text-center py-8 text-xs text-rose">${err.message}</div>`
  }
}

// ── RENDERIZADO DE RESULTADOS ML ──────────────────────────────────────────

function _renderMLResults(a) {
  if (a.status !== 'completed' || !a.top1_label) {
    return `<div class="info-box text-[11px]">Resultados no disponibles.</div>`
  }

  const r          = a.result || {}
  const condition  = r.condition  || a.top1_label
  const confidence = r.confidence ?? a.top1_confidence ?? 0
  const confPct    = Math.round(confidence * 100)
  const condLabel  = _LABEL_ES[condition] || condition
  const desc       = _DESCRIPCIONES[condition] || ''
  const severity   = r.severity_score ?? 0
  const sevPct     = Math.round(severity * 100)
  const worstZone  = r.worst_zone ? (_ZONE_ES[r.worst_zone] || r.worst_zone) : '—'
  const zonesCount = r.affected_zones_count ?? 0

  const _sevBg    = v => v < 0.25 ? 'bg-ok'    : v < 0.5 ? 'bg-warn'    : 'bg-rose'
  const _sevText  = v => v < 0.25 ? 'text-ok'  : v < 0.5 ? 'text-warn'  : 'text-rose'
  const _sevLabel = v => v < 0.25 ? 'Leve'     : v < 0.5 ? 'Moderado'   : 'Alto'
  const confBg    = confPct >= 60  ? 'bg-forest' : confPct >= 40 ? 'bg-warn' : 'bg-slate/40'
  const confText  = confPct >= 60  ? 'text-forest' : confPct >= 40 ? 'text-warn' : 'text-slate'

  // ── 1. Diagnóstico principal ─────────────────────────────────────────────
  const diagHTML = `
    <div class="bg-gradient-to-br from-forest/8 to-forest/3 border border-forest/20 rounded-2xl p-4 mb-3">
      <p class="text-[9px] text-forest uppercase tracking-widest font-semibold mb-2">
        Diagnóstico principal
      </p>
      <p class="text-[17px] font-bold text-ink leading-snug">${condLabel}</p>
      ${desc ? `<p class="text-[11px] text-slate mt-1 leading-relaxed">${desc}</p>` : ''}
      <div class="mt-3">
        <div class="flex justify-between items-center mb-1">
          <span class="text-[10px] text-slate">Confianza del modelo</span>
          <span class="text-[13px] font-bold ${confText}">${confPct}%</span>
        </div>
        <div class="w-full bg-sand rounded-full h-2">
          <div class="${confBg} h-2 rounded-full transition-all" style="width:${confPct}%"></div>
        </div>
      </div>
    </div>`

  // ── 2. Severidad + zona + conteo ─────────────────────────────────────────
  const statsHTML = `
    <div class="grid grid-cols-3 gap-2 mb-3">
      <div class="bg-sand/50 rounded-xl p-3 text-center">
        <p class="text-[9px] text-slate uppercase tracking-widest mb-1">Severidad</p>
        <p class="text-[18px] font-bold ${_sevText(severity)}">${sevPct}%</p>
        <p class="text-[9px] ${_sevText(severity)} font-medium mt-0.5">${_sevLabel(severity)}</p>
        <div class="w-full bg-sand rounded-full h-1 mt-1.5">
          <div class="${_sevBg(severity)} h-1 rounded-full" style="width:${sevPct}%"></div>
        </div>
      </div>
      <div class="bg-sand/50 rounded-xl p-3 text-center col-span-2 flex flex-col justify-center">
        <p class="text-[9px] text-slate uppercase tracking-widest mb-1">Zona más afectada</p>
        <p class="text-[13px] font-bold text-ink leading-tight">${worstZone}</p>
        <p class="text-[9px] text-slate mt-1.5">
          ${zonesCount} zona${zonesCount !== 1 ? 's' : ''} activa${zonesCount !== 1 ? 's' : ''}
        </p>
      </div>
    </div>`

  // ── 3. Top N condiciones ──────────────────────────────────────────────────
  let topNHTML = ''
  if (r.top_n?.length) {
    topNHTML = `
      <div class="bg-sand/30 rounded-2xl p-3 mb-3">
        <p class="text-[9px] text-slate uppercase tracking-widest font-semibold mb-2">
          Condiciones detectadas
        </p>
        ${r.top_n.map((item, i) => {
          const pct   = Math.round(item.prob * 100)
          const name  = _LABEL_ES[item.label] || item.label
          const isTop = i === 0
          return `
            <div class="flex items-center gap-2 py-1.5 ${i < r.top_n.length - 1 ? 'border-b border-sand' : ''}">
              <span class="text-[9px] text-slate/50 w-4 flex-shrink-0">${i + 1}</span>
              <div class="flex-1 min-w-0">
                <p class="text-[11px] ${isTop ? 'font-semibold text-ink' : 'text-ink/65'} truncate">${name}</p>
                <div class="w-full bg-sand rounded-full h-1 mt-0.5">
                  <div class="${isTop ? 'bg-forest' : 'bg-slate/30'} h-1 rounded-full" style="width:${pct}%"></div>
                </div>
              </div>
              <span class="text-[11px] ${isTop ? 'font-bold text-forest' : 'text-slate'} w-8 text-right flex-shrink-0">
                ${pct}%
              </span>
            </div>`
        }).join('')}
      </div>`
  }

  // ── 4. Zonas principales ─────────────────────────────────────────────────
  let zonesDisplayHTML = ''
  const zonesDisp = r.zones_display || {}
  if (Object.keys(zonesDisp).length) {
    zonesDisplayHTML = `
      <div class="mb-3">
        <p class="text-[9px] text-slate uppercase tracking-widest font-semibold mb-2">
          Zonas principales
        </p>
        <div class="space-y-2">
          ${Object.entries(zonesDisp).map(([zona, m]) => {
            const name    = _ZONE_ES[zona] || zona
            const zSev    = Math.round(m.severity * 100)
            const eritPct = Math.round((m.erythema  ?? 0) * 100)
            const comPct  = Math.round((m.comedones ?? 0) * 100)
            const scaPct  = Math.round((m.scaling ?? m.descamacion ?? 0) * 100)
            return `
              <div class="bg-sand/40 rounded-xl p-3">
                <div class="flex justify-between items-center mb-1.5">
                  <span class="text-[11px] font-medium text-ink">${name}</span>
                  <span class="text-[11px] font-bold ${_sevText(m.severity)}">${_sevLabel(m.severity)} · ${zSev}%</span>
                </div>
                <div class="w-full bg-sand rounded-full h-1.5 mb-2">
                  <div class="${_sevBg(m.severity)} h-1.5 rounded-full" style="width:${zSev}%"></div>
                </div>
                <div class="flex gap-1.5 flex-wrap">
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">
                    eritema ${eritPct}%
                  </span>
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">
                    comedones ${comPct}%
                  </span>
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">
                    escamas ${scaPct}%
                  </span>
                </div>
              </div>`
          }).join('')}
        </div>
      </div>`
  }

  // ── 5. Subzonas diagnósticas ─────────────────────────────────────────────
  let zonesDiagHTML = ''
  const zonesDiag = r.zones_diagnostic || {}
  if (Object.keys(zonesDiag).length) {
    zonesDiagHTML = `
      <div class="mb-1">
        <p class="text-[9px] text-slate uppercase tracking-widest font-semibold mb-2">
          Subzonas diagnósticas
        </p>
        <div class="grid grid-cols-2 gap-1.5">
          ${Object.entries(zonesDiag).map(([zona, m]) => {
            const name    = _ZONE_ES[zona] || zona
            const zSev    = Math.round(m.severity * 100)
            const eritPct = Math.round((m.erythema  ?? 0) * 100)
            const comPct  = Math.round((m.comedones ?? 0) * 100)
            return `
              <div class="bg-sand/40 rounded-xl p-2.5">
                <p class="text-[10px] font-medium text-ink leading-tight mb-1.5">${name}</p>
                <div class="flex justify-between items-center mb-1">
                  <span class="text-[9px] text-slate">Sev.</span>
                  <span class="text-[10px] font-bold ${_sevText(m.severity)}">${zSev}%</span>
                </div>
                <div class="w-full bg-sand rounded-full h-1 mb-1.5">
                  <div class="${_sevBg(m.severity)} h-1 rounded-full" style="width:${zSev}%"></div>
                </div>
                <div class="flex gap-1 flex-wrap">
                  <span class="text-[8px] bg-white/70 rounded-full px-1.5 py-0.5 text-slate/70">
                    er ${eritPct}%
                  </span>
                  <span class="text-[8px] bg-white/70 rounded-full px-1.5 py-0.5 text-slate/70">
                    co ${comPct}%
                  </span>
                </div>
              </div>`
          }).join('')}
        </div>
      </div>`
  }

  return `${diagHTML}${statsHTML}${topNHTML}${zonesDisplayHTML}${zonesDiagHTML}`
}

function _renderDetail(a, container, userNum) {
  const token = localStorage.getItem('skinai_token')
  const dateStr = _formatDate(a.created_at)

  const statusBadge = a.status === 'completed'
    ? '<span class="bg-ok/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Completado</span>'
    : a.status === 'failed'
    ? '<span class="bg-rose/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Error</span>'
    : '<span class="bg-warn/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">Procesando</span>'

  const imgSection = a.censored_filename || a.original_filename
    ? `<img
         src="${API}/analysis/${a.id}/image?token=${token}"
         alt="Imagen procesada análisis #${userNum}"
         class="w-full h-auto block"
         onerror="this.parentElement.innerHTML='<p class=\\'text-xs text-slate text-center py-8\\'>Imagen no disponible</p>'"
       >`
    : '<p class="text-xs text-slate text-center py-8">Sin imagen</p>'

  container.innerHTML = `
    <!-- Volver -->
    <button class="btn-back-dark mb-4 text-sm" onclick="closeDetail()">
      ← Volver al historial
    </button>

    <!-- Cabecera -->
    <div class="bg-gradient-diag rounded-card p-4 text-white mb-4">
      <div class="flex items-center justify-between mb-1.5">
        <span class="bg-white/15 rounded-md px-2 py-0.5 text-[11px] font-bold">
          Análisis #${userNum}
        </span>
        ${statusBadge}
      </div>
      <h2 class="font-display text-lg text-cream mb-0.5">
        ${_LABEL_ES[a.top1_label] || 'Análisis de piel'}
      </h2>
      <p class="text-[11px] text-white/55">${dateStr}</p>
    </div>

    <!-- Imagen procesada -->
    <div class="card card-body mb-4">
      <p class="section-label mb-2">Imagen procesada</p>
      <div class="rounded-xl overflow-hidden mb-2">
        ${imgSection}
      </div>
      <p class="text-[10px] text-slate leading-relaxed">
        Los ojos fueron difuminados automáticamente para proteger tu privacidad
        antes de ser procesada por el modelo.
      </p>
    </div>

    <!-- Resultados ML -->
    <div class="card card-body mb-4">
      <p class="section-label mb-3">Resultados del modelo ML</p>
      ${_renderMLResults(a)}
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
