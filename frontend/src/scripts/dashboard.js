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
let _recoData        = null // cache del último response de recomendaciones
let _recoCondIdx     = 0    // condición activa en el panel de recomendaciones
let _dashRecoData    = null // cache de recomendaciones del dashboard
let _dashRecoCondIdx = 0    // condición activa en el card del dashboard

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

const _ZONE_CHILDREN = {
  frente:      ['ceja_izq',      'ceja_der'],
  nariz:       ['nariz_lat_izq', 'nariz_lat_der'],
  menton:      ['zona_perioral'],
  mejilla_izq: ['mandibula_izq'],
  mejilla_der: ['mandibula_der'],
}

const _CATEGORY_ES = {
  cleanser:    'Limpiador',
  moisturizer: 'Hidratante',
  spf:         'Protector solar',
  serum:       'Sérum',
  exfoliant:   'Exfoliante',
  retinoid:    'Retinoide',
  spot:        'Tratamiento puntual',
  toner:       'Tónico',
  eye:         'Contorno de ojos',
  mask:        'Mascarilla',
  oil:         'Aceite facial',
}
const _CAT_DESC = {
  cleanser:    'Primer paso · mañana y noche',
  moisturizer: 'Hidratación y barrera',
  spf:         'Protección solar · cada mañana',
  serum:       'Activos concentrados',
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
    _populateComparisonTab(analyses)
    _populateHistoryTab(analyses)
    _populateRoutineTab(routine)

    window._skinaiAnalyses = analyses
    import('./charts.js').then(m => m.initCharts())
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

// ── MAPA FACIAL SVG ───────────────────────────────────────────────────────

function _zoneColor(severity) {
  if (severity == null) return '#D4C9B8'
  if (severity < 0.25)  return '#2E7D5A'
  if (severity < 0.50)  return '#D4942A'
  if (severity < 0.75)  return '#C47060'
  return '#8B2A1A'
}

function _updateFacialMap(result) {
  const svg = document.getElementById('facial-map-svg')
  if (!svg) return

  const zones = {
    ...(result?.zones_display    || {}),
    ...(result?.zones_diagnostic || {}),
  }

  svg.querySelectorAll('[data-zone]').forEach(el => {
    const data = zones[el.getAttribute('data-zone')]
    el.setAttribute('fill', _zoneColor(data?.severity ?? null))
    el.setAttribute('fill-opacity', data ? '0.55' : '0.25')
  })
}

// ── HERO HELPERS ──────────────────────────────────────────────────────────

function _sevLevelInfo(v) {
  if (v < 0.10) return { label: 'Sin señales', adj: 'mínimas',   stroke: '#9CA3AF', textColor: 'text-slate',      colorInk: 'text-slate' }
  if (v < 0.25) return { label: 'Leve',        adj: 'leves',     stroke: '#5FBA8B', textColor: 'text-[#5FBA8B]', colorInk: 'text-ok' }
  if (v < 0.50) return { label: 'Moderada',    adj: 'moderadas', stroke: '#D4942A', textColor: 'text-bark',       colorInk: 'text-warn' }
  if (v < 0.75) return { label: 'Alta',        adj: 'altas',     stroke: '#E8906A', textColor: 'text-[#E8906A]', colorInk: 'text-[#C96A40]' }
  return               { label: 'Severa',      adj: 'severas',   stroke: '#C47060', textColor: 'text-rose',       colorInk: 'text-rose' }
}

function _confLabel(c) {
  return c >= 0.70 ? 'Alta' : c >= 0.50 ? 'Media' : 'Baja'
}

function _confText(c) {
  return c >= 0.70 ? 'Este resultado es confiable.'
       : c >= 0.50 ? 'El resultado puede variar.'
       :              'El resultado tiene baja certeza.'
}

function _relativeTime(isoStr) {
  if (!isoStr) return '--'
  const days = Math.floor((Date.now() - new Date(isoStr).getTime()) / 86400000)
  if (days === 0) return 'Hoy'
  if (days === 1) return 'Hace 1 día'
  return `Hace ${days} días`
}

function _formatDateShort(isoStr) {
  if (!isoStr) return '--'
  try {
    return new Date(isoStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return isoStr }
}

function _donutSVG(pct, stroke, sizeClass = 'w-11 h-11', dark = true) {
  const trackColor  = dark ? 'rgba(255,255,255,0.12)' : '#E8E2D6'
  const textColor   = dark ? 'white' : '#181C24'
  return `<svg viewBox="0 0 36 36" class="${sizeClass} mx-auto" aria-hidden="true">
    <circle cx="18" cy="18" r="15.9155" fill="none" stroke="${trackColor}" stroke-width="3"/>
    <circle cx="18" cy="18" r="15.9155" fill="none" stroke="${stroke}" stroke-width="3"
      stroke-dasharray="${pct} 100" stroke-linecap="round" transform="rotate(-90 18 18)"/>
    <text x="18" y="22" text-anchor="middle" fill="${textColor}" font-size="8" font-weight="bold"
      font-family="DM Sans,sans-serif">${pct}%</text>
  </svg>`
}

function _miniFaceSVG(worstZone) {
  // Coordenadas en el sistema 682×870 de rostro-base.png
  const zones = {
    frente:        { cx: 341, cy: 165, rx: 170, ry: 130 },
    ceja_izq:      { cx: 250, cy: 310, rx: 56,  ry: 20  },
    ceja_der:      { cx: 432, cy: 310, rx: 56,  ry: 20  },
    mejilla_izq:   { cx: 155, cy: 560, rx: 68,  ry: 118 },
    mejilla_der:   { cx: 527, cy: 560, rx: 68,  ry: 118 },
    nariz:         { cx: 341, cy: 482, rx: 46,  ry: 102 },
    nariz_lat_izq: { cx: 291, cy: 575, rx: 27,  ry: 22  },
    nariz_lat_der: { cx: 391, cy: 575, rx: 27,  ry: 22  },
    zona_perioral: { cx: 341, cy: 638, rx: 80,  ry: 48  },
    mandibula_izq: { cx: 193, cy: 733, rx: 70,  ry: 57  },
    mandibula_der: { cx: 489, cy: 733, rx: 70,  ry: 57  },
    menton:        { cx: 341, cy: 810, rx: 108, ry: 42  },
  }
  const worstEllipse = worstZone && zones[worstZone]
    ? `<ellipse cx="${zones[worstZone].cx}" cy="${zones[worstZone].cy}"
         rx="${zones[worstZone].rx}" ry="${zones[worstZone].ry}"
         fill="#C47060" fill-opacity="0.65"/>`
    : ''
  return `
    <div class="relative w-14 mx-auto select-none my-1">
      <img src="/img-resource/rostro-base.png" alt="" class="w-full h-auto block pointer-events-none" draggable="false">
      <svg viewBox="0 0 682 870" preserveAspectRatio="none"
           class="absolute inset-0 w-full h-full pointer-events-none" aria-hidden="true">
        <defs>
          <clipPath id="kpi-face-clip">
            <ellipse cx="341" cy="440" rx="225" ry="400"/>
          </clipPath>
        </defs>
        <g clip-path="url(#kpi-face-clip)">${worstEllipse}</g>
      </svg>
    </div>`
}

// ── TAB: DASHBOARD (resumen) ──────────────────────────────────────────────

function _populateDashTab(analyses) {
  const latestEl = document.getElementById('dash-latest')
  if (!latestEl) return

  _updateFacialMap(analyses[0]?.result ?? null)

  const latest = analyses[0]
  if (!latest) return

  const result   = latest.result || {}
  const label    = _LABEL_ES[latest.top1_label] || 'Análisis completado'
  const conf     = latest.top1_confidence ?? 0
  const confPct  = Math.round(conf * 100)
  const sev      = result.severity_score ?? 0
  const sevPct   = Math.round(sev * 100)
  const sevInfo  = _sevLevelInfo(sev)
  const worstZone = result.worst_zone ? (_ZONE_ES[result.worst_zone] || result.worst_zone) : '—'
  const zonesCount = result.affected_zones_count ?? 0
  const dateShort  = _formatDateShort(latest.created_at)
  const relTime    = _relativeTime(latest.created_at)

  // ── Estado actual (green card) ───────────────────────────────────────────
  latestEl.innerHTML = `
    <div class="flex items-center gap-1.5 mb-3">
      <svg class="w-3.5 h-3.5 flex-shrink-0 text-[#5FBA8B]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
      </svg>
      <p class="text-[9px] text-white/60 uppercase tracking-widest font-semibold">Estado actual</p>
    </div>
    <h2 class="font-display text-xl text-cream leading-snug mb-1.5">
      Detectamos señales <span class="${sevInfo.textColor}">${sevInfo.adj}</span> de ${label}
    </h2>
    <p class="text-[11px] text-white/55 leading-relaxed mb-auto pb-4">Detectamos acné y rosácea desde una foto de tu rostro y te recomendamos una rutina con productos reales.</p>
    <div class="flex gap-2 mt-auto">
      <button class="flex-1 flex items-center justify-center gap-2 bg-white text-forest text-sm font-semibold py-2.5 px-4 rounded-full hover:bg-white/90 transition-colors" data-go="capture">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><circle cx="12" cy="13" r="3"/></svg>
        Nuevo análisis
      </button>
      <button class="flex-1 flex items-center justify-center gap-2 bg-white/15 text-white text-sm font-semibold py-2.5 px-4 rounded-full hover:bg-white/25 transition-colors" onclick="dtab('dh')">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        Ver último análisis
      </button>
    </div>`

  // ── KPI: Severidad global ────────────────────────────────────────────────
  const kpiSev = document.getElementById('kpi-sev')
  if (kpiSev) {
    kpiSev.innerHTML = `
      <p class="text-[9px] text-slate/65 uppercase tracking-widest font-semibold">Severidad global</p>
      <div class="my-1">${_donutSVG(sevPct, sevInfo.stroke, 'w-16 h-16', false)}</div>
      <div>
        <p class="text-sm font-bold ${sevInfo.colorInk} leading-tight">${sevInfo.label}</p>
        <p class="text-[9px] text-slate/55 mt-0.5">Resultado ${confPct >= 70 ? 'confiable' : 'variable'}</p>
      </div>`
    kpiSev.classList.remove('hidden')
  }

  // ── KPI: Zona más afectada ───────────────────────────────────────────────
  const kpiZone = document.getElementById('kpi-zone')
  if (kpiZone) {
    kpiZone.innerHTML = `
      <p class="text-[9px] text-slate/65 uppercase tracking-widest font-semibold">Zona más afectada</p>
      ${_miniFaceSVG(result.worst_zone)}
      <div>
        <p class="text-base font-bold text-rose leading-tight">${worstZone}</p>
        <p class="text-[9px] text-slate/55 mt-0.5">Principales señales aquí</p>
      </div>`
    kpiZone.classList.remove('hidden')
  }

  // ── KPI: Zonas afectadas ─────────────────────────────────────────────────
  const kpiZones = document.getElementById('kpi-zones')
  if (kpiZones) {
    kpiZones.innerHTML = `
      <p class="text-[9px] text-slate/65 uppercase tracking-widest font-semibold">Zonas afectadas</p>
      <svg class="w-10 h-10 mx-auto my-1" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="10" cy="10" r="5" fill="#D4942A" opacity="0.9"/>
        <circle cx="30" cy="10" r="5" fill="#D4942A" opacity="0.9"/>
        <circle cx="10" cy="30" r="5" fill="#D4942A" opacity="0.4"/>
        <circle cx="30" cy="30" r="5" fill="#D4942A" opacity="0.4"/>
        <circle cx="10" cy="20" r="5" fill="#D4942A" opacity="0.65"/>
        <circle cx="30" cy="20" r="5" fill="#D4942A" opacity="0.65"/>
      </svg>
      <div>
        <p class="text-xl font-bold text-warn leading-none">${zonesCount}<span class="text-sm text-slate/50 font-semibold">/12</span></p>
        <p class="text-[9px] text-slate/55 mt-0.5">Con señales activas</p>
      </div>`
    kpiZones.classList.remove('hidden')
  }

  // ── KPI: Último análisis ─────────────────────────────────────────────────
  const kpiDate = document.getElementById('kpi-date')
  if (kpiDate) {
    kpiDate.innerHTML = `
      <p class="text-[9px] text-slate/65 uppercase tracking-widest font-semibold">Último análisis</p>
      <svg class="w-10 h-10 mx-auto my-1" fill="none" stroke="#4F6FAD" stroke-width="1.6" viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <div>
        <p class="text-sm font-bold text-[#4F6FAD] leading-tight">${dateShort}</p>
        <p class="text-[9px] text-slate/55 mt-0.5">${relTime}</p>
      </div>`
    kpiDate.classList.remove('hidden')
  }

  if (latest.status === 'completed') {
    _populateDashRecommendations(latest)
  }
}

async function _populateDashRecommendations(latest) {
  const el = document.getElementById('dash-recommendations')
  if (!el) return

  const token = localStorage.getItem('skinai_token')

  el.innerHTML = `
    <p class="section-label mb-2">Recomendaciones</p>
    <div class="flex items-center justify-center gap-2 py-6 text-[11px] text-slate">
      <svg class="w-4 h-4 animate-spin flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
      </svg>
      Cargando...
    </div>`

  try {
    const res = await fetch(`${API}/products/recommendations/${latest.id}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!res.ok) throw new Error()
    const data = await res.json()

    const conds   = data.conditions || []
    const primary = conds[0]
    if (!primary) throw new Error()

    const reco = primary.recommendations || {}

    _dashRecoData    = data
    _dashRecoCondIdx = 0

    const condPillsHTML = conds.length > 1
      ? conds.map((c, i) => {
          const name = _LABEL_ES[c.condition] || c.condition
          const pct  = Math.round((c.confidence || 0) * 100)
          return `<button id="dash-reco-pill-${i}" onclick="switchDashReco(${i})"
            class="text-[8px] rounded-full px-2 py-0.5 font-medium transition-colors ${i === 0 ? 'bg-forest text-white' : 'bg-forest/10 text-forest hover:bg-forest/20'}">${name} · ${pct}%</button>`
        }).join('')
      : `<span class="text-[8px] text-forest bg-forest/10 rounded-full px-2 py-0.5 font-medium">${_LABEL_ES[conds[0].condition] || conds[0].condition} · ${Math.round((conds[0].confidence || 0) * 100)}%</span>`

    const rowsHTML = _dashRecoRows(reco)
    if (!rowsHTML) throw new Error()

    el.innerHTML = `
      <p class="section-label mb-2">Recomendaciones</p>
      <div class="flex flex-wrap gap-1 mb-2.5">
        ${condPillsHTML}
      </div>
      <div id="dash-reco-rows" class="bg-sand/30 rounded-xl px-2.5 py-0.5 mb-3">
        ${rowsHTML}
      </div>
      <button onclick="dtab('dh'); openDetail(${latest.id})"
        class="w-full text-[11px] text-forest font-semibold flex items-center justify-center gap-1 py-2 bg-forest/5 rounded-xl hover:bg-forest/10 transition-colors">
        Ver completas en historial
        <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </button>`

  } catch {
    el.innerHTML = `
      <p class="section-label mb-2">Recomendaciones</p>
      <p class="text-[11px] text-slate text-center py-4">No se pudieron cargar las recomendaciones.</p>`
  }
}

function _dashRecoRows(reco) {
  const CATS = ['cleanser', 'moisturizer', 'spf', 'serum']
  return CATS.flatMap(cat => {
    const p = (reco[cat] || [])[0]
    if (!p) return []
    const si    = _scoreInfo(p.score || 0)
    const catES = _CATEGORY_ES[cat] || cat
    return [`
      <div class="flex items-center gap-2 py-1.5 border-b border-sand/60 last:border-0">
        <span class="text-[8px] text-slate/55 font-bold uppercase tracking-wide w-16 flex-shrink-0">${catES}</span>
        <p class="text-[11px] text-ink font-medium flex-1 truncate min-w-0">${p.name}</p>
        <span class="text-[8px] font-semibold ${si.bg} ${si.color} rounded-full px-1.5 py-0.5 flex-shrink-0">${si.label}</span>
      </div>`]
  }).join('')
}

export function switchDashReco(idx) {
  if (!_dashRecoData) return
  _dashRecoCondIdx = idx

  const conds = _dashRecoData.conditions || []
  const cond  = conds[idx] || conds[0]

  const rowsEl = document.getElementById('dash-reco-rows')
  if (rowsEl) rowsEl.innerHTML = _dashRecoRows(cond.recommendations || {})

  conds.forEach((_, i) => {
    const pill = document.getElementById(`dash-reco-pill-${i}`)
    if (!pill) return
    pill.className = `text-[8px] rounded-full px-2 py-0.5 font-medium transition-colors ${
      i === idx ? 'bg-forest text-white' : 'bg-forest/10 text-forest hover:bg-forest/20'
    }`
  })
}
window.switchDashReco = switchDashReco

// ── TAB: COMPARACIÓN ─────────────────────────────────────────────────────

function _avgZone(result, key) {
  const zones = Object.values(result?.zones_display || {})
  if (!zones.length) return 0
  return zones.reduce((s, z) => s + (z[key] ?? 0), 0) / zones.length
}

function _populateComparisonTab(analyses) {
  const el   = document.getElementById('dash-comparison')
  const body = document.getElementById('dash-comparison-body')
  if (!el || !body) return

  const curr = analyses[0]
  const prev = analyses[1]
  if (!curr?.result || !prev?.result) return

  el.classList.remove('hidden')

  const _ICONS = {
    sev:   `<svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>`,
    erit:  `<svg class="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24"><circle cx="5" cy="5" r="2"/><circle cx="12" cy="4" r="2"/><circle cx="19" cy="7" r="2"/><circle cx="7" cy="12" r="2"/><circle cx="15" cy="13" r="2"/><circle cx="10" cy="19" r="2"/><circle cx="18" cy="18" r="2"/></svg>`,
    com:   `<svg class="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="5" height="5" rx="1"/><rect x="9.5" y="3" width="5" height="5" rx="1"/><rect x="16" y="3" width="5" height="5" rx="1"/><rect x="3" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><rect x="16" y="9.5" width="5" height="5" rx="1"/><rect x="3" y="16" width="5" height="5" rx="1"/><rect x="9.5" y="16" width="5" height="5" rx="1"/><rect x="16" y="16" width="5" height="5" rx="1"/></svg>`,
    tex:   `<svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M3 7c2-2 4 2 6 0s4-2 6 0 4 2 6 0M3 13c2-2 4 2 6 0s4-2 6 0 4 2 6 0M3 19c2-2 4 2 6 0s4-2 6 0 4 2 6 0"/></svg>`,
    zones: `<svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><ellipse cx="12" cy="8" rx="5" ry="4" stroke-width="1.8"/><path stroke-linecap="round" stroke-width="1.8" d="M7 12c-2 1-3 3-3 5h16c0-2-1-4-3-5"/></svg>`,
  }

  const rows = [
    { label: 'Severidad global',  icon: _ICONS.sev,   prev: Math.round((prev.result.severity_score ?? 0) * 100), curr: Math.round((curr.result.severity_score ?? 0) * 100), unit: '%',  max: 100 },
    { label: 'Enrojecimiento',    icon: _ICONS.erit,  prev: Math.round(_avgZone(prev.result, 'erythema')   * 100), curr: Math.round(_avgZone(curr.result, 'erythema')   * 100), unit: '%',  max: 100 },
    { label: 'Comedones',         icon: _ICONS.com,   prev: Math.round(_avgZone(prev.result, 'comedones')  * 100), curr: Math.round(_avgZone(curr.result, 'comedones')  * 100), unit: '%',  max: 100 },
    { label: 'Textura / Escamas', icon: _ICONS.tex,   prev: Math.round(_avgZone(prev.result, 'scaling')    * 100), curr: Math.round(_avgZone(curr.result, 'scaling')    * 100), unit: '%',  max: 100 },
    { label: 'Zonas afectadas',   icon: _ICONS.zones, prev: prev.result.affected_zones_count ?? 0,                 curr: curr.result.affected_zones_count ?? 0,                 unit: ' z', max: 12  },
  ]

  const headerHTML = `
    <div class="grid grid-cols-[1fr_auto_auto_auto] gap-2 pb-2 border-b border-sand mb-1">
      <span class="text-[8px] text-slate/60 uppercase tracking-wide">Indicador</span>
      <span class="text-[8px] text-slate/60 uppercase tracking-wide w-16 text-center">Anterior</span>
      <span class="text-[8px] text-slate/60 uppercase tracking-wide w-16 text-center">Actual</span>
      <span class="text-[8px] text-slate/60 uppercase tracking-wide w-12 text-right">Cambio</span>
    </div>`

  const rowsHTML = rows.map(r => {
    const delta     = r.curr - r.prev
    const deltaPct  = r.prev > 0 ? Math.round(Math.abs(delta / r.prev) * 100) : (r.curr > 0 ? 100 : 0)
    const improved  = delta < 0
    const unchanged = delta === 0
    const changeClass = unchanged ? 'text-slate' : improved ? 'text-ok' : 'text-rose'
    const changeText  = unchanged ? '—' : `${improved ? '↓' : '↑'} ${deltaPct}%`
    const prevW = Math.min(100, Math.round((r.prev / r.max) * 100))
    const currW = Math.min(100, Math.round((r.curr / r.max) * 100))
    const currBarClass = improved ? 'bg-ok' : unchanged ? 'bg-slate/35' : 'bg-rose'

    return `
      <div class="grid grid-cols-[1fr_auto_auto_auto] gap-2 items-center py-1.5 border-b border-sand/60 last:border-0">
        <div class="flex items-center gap-1.5 min-w-0 text-slate">
          ${r.icon}
          <span class="text-[10px] font-semibold text-ink truncate">${r.label}</span>
        </div>
        <div class="w-16">
          <p class="text-[8px] text-slate text-center mb-0.5">${r.prev}${r.unit}</p>
          <div class="w-full bg-sand rounded-full h-1.5">
            <div class="h-1.5 rounded-full bg-slate/40" style="width:${prevW}%"></div>
          </div>
        </div>
        <div class="w-16">
          <p class="text-[8px] text-slate text-center mb-0.5">${r.curr}${r.unit}</p>
          <div class="w-full bg-sand rounded-full h-1.5">
            <div class="h-1.5 rounded-full ${currBarClass}" style="width:${currW}%"></div>
          </div>
        </div>
        <span class="text-[10px] font-bold ${changeClass} w-12 text-right flex-shrink-0">${changeText}</span>
      </div>`
  }).join('')

  body.innerHTML = `
    <p class="text-[8px] text-slate uppercase tracking-widest font-semibold mb-2">
      ${_formatDate(prev.created_at)} → ${_formatDate(curr.created_at)}
    </p>
    ${headerHTML}
    ${rowsHTML}
    <p class="text-[9px] text-slate/50 mt-2">Los cambios se calculan del análisis anterior al actual.</p>`
}

// ── TAB: HISTORIAL ────────────────────────────────────────────────────────

function _condIconHTML(condKey) {
  const styles = {
    'healthy-skin':          ['#E8F5EE', '#2E7D5A'],
    'acne-comedonal':        ['#FEF3C7', '#B45309'],
    'acne-excoriated':       ['#FEF3C7', '#B45309'],
    'acne-inflammatory':     ['#FEE2E2', '#DC2626'],
    'perioral-dermatitis':   ['#FDECD0', '#C2410C'],
    'rosacea-etr':           ['#FEE2E2', '#DC2626'],
    'rosacea-inflammatory':  ['#FEE2E2', '#B91C1C'],
    'seborrheic-dermatitis': ['#FDECD0', '#C2410C'],
  }
  const [bg, stroke] = styles[condKey] || ['#F0EDE8', '#6B5E4E']
  return `<div style="background:${bg}" class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0">
    <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="${stroke}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="8" r="4"/><path d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
    </svg>
  </div>`
}

function _sevInfoHist(v) {
  if (v < 0.20) return { label: 'Leve',     textColor: 'text-ok',         barColor: 'bg-ok' }
  if (v < 0.50) return { label: 'Moderado', textColor: 'text-warn',       barColor: 'bg-warn' }
  if (v < 0.75) return { label: 'Alto',     textColor: 'text-[#E8906A]',  barColor: 'bg-[#E8906A]' }
  return               { label: 'Severo',   textColor: 'text-rose',       barColor: 'bg-rose' }
}

function _histZoneData(a) {
  const r         = a.result || {}
  const zonesDisp = r.zones_display || {}
  const entries   = Object.entries(zonesDisp)
  const worstKey  = r.worst_zone || null
  const worstName = worstKey ? (_ZONE_ES[worstKey] || worstKey) : '—'
  const worstPct  = worstKey && zonesDisp[worstKey]
    ? Math.round((zonesDisp[worstKey].severity ?? 0) * 100) : null
  let bestName = '—', bestPct = null
  if (entries.length) {
    const [bKey, bVal] = entries.reduce((mn, cur) =>
      (cur[1].severity ?? 1) < (mn[1].severity ?? 1) ? cur : mn)
    bestName = _ZONE_ES[bKey] || bKey
    bestPct  = Math.round((bVal.severity ?? 0) * 100)
  }
  return { worstName, worstPct, bestName, bestPct }
}

const _MO = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']

function _histDateStr(isoStr) {
  const d = new Date(isoStr)
  return `${d.getDate()} ${_MO[d.getMonth()]} ${d.getFullYear()}`
}

function _histTableRow(a) {
  const userNum = _analysisUserNum[a.id] || '?'
  const condKey = a.top1_label || ''
  const label   = _LABEL_ES[condKey] || 'Análisis de piel'
  const r       = a.result || {}
  const sev     = r.severity_score ?? 0
  const sevPct  = Math.round(sev * 100)
  const sevI    = _sevInfoHist(sev)
  const { worstName, worstPct, bestName, bestPct } = _histZoneData(a)

  return `
    <tr class="border-b border-sand hover:bg-sand/20 transition-colors">
      <td class="px-4 py-3.5">
        <span class="text-[11px] font-bold text-ink bg-sand/60 rounded-lg px-2.5 py-1 whitespace-nowrap">#${userNum}</span>
      </td>
      <td class="px-4 py-3.5">
        <div class="flex items-center gap-3">
          ${_condIconHTML(condKey)}
          <span class="text-[12px] font-semibold text-ink whitespace-nowrap">${label}</span>
        </div>
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <p class="text-[12px] font-semibold ${sevI.textColor}">${sevI.label} ${sevPct}%</p>
        <div class="w-24 bg-sand rounded-full h-1.5 mt-1.5">
          <div class="${sevI.barColor} h-1.5 rounded-full" style="width:${sevPct}%"></div>
        </div>
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <p class="text-[12px] font-medium text-ink">${worstName}</p>
        ${worstPct != null ? `<p class="text-[11px] text-slate mt-0.5">${worstPct}%</p>` : ''}
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <p class="text-[12px] font-medium text-ink">${bestName}</p>
        ${bestPct != null ? `<p class="text-[11px] text-slate mt-0.5">${bestPct}%</p>` : ''}
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <span class="inline-flex items-center gap-1 text-[11px] font-semibold text-ok bg-ok/10 rounded-full px-3 py-1">
          <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          Completado
        </span>
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <span class="text-[12px] text-slate">${_histDateStr(a.created_at)}</span>
      </td>
      <td class="px-4 py-3.5 whitespace-nowrap">
        <button onclick="openDetail(${a.id})"
          class="flex items-center gap-1.5 text-[11px] font-semibold text-slate hover:text-ink transition-colors">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          Ver análisis
        </button>
      </td>
    </tr>`
}

function _histCard(a) {
  const userNum = _analysisUserNum[a.id] || '?'
  const condKey = a.top1_label || ''
  const label   = _LABEL_ES[condKey] || 'Análisis de piel'
  const r       = a.result || {}
  const sev     = r.severity_score ?? 0
  const sevPct  = Math.round(sev * 100)
  const sevI    = _sevInfoHist(sev)
  const { worstName, worstPct, bestName, bestPct } = _histZoneData(a)

  return `
    <div class="bg-white rounded-2xl border border-sand p-4">
      <div class="flex items-center justify-between mb-3">
        <span class="text-[11px] font-bold text-ink bg-sand/60 rounded-lg px-2.5 py-1">#${userNum}</span>
        <div class="flex items-center gap-1.5">
          <span class="inline-flex items-center gap-1 text-[10px] font-semibold text-ok">
            <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            Completado
          </span>
          <span class="text-[10px] text-slate">${_histDateStr(a.created_at)}</span>
        </div>
      </div>
      <div class="flex items-center gap-3 mb-3">
        ${_condIconHTML(condKey)}
        <p class="text-[16px] font-bold text-ink leading-tight">${label}</p>
      </div>
      <p class="text-[13px] font-semibold ${sevI.textColor} mb-1">${sevI.label} ${sevPct}%</p>
      <div class="w-full bg-sand rounded-full h-1.5 mb-4">
        <div class="${sevI.barColor} h-1.5 rounded-full" style="width:${sevPct}%"></div>
      </div>
      <div class="grid grid-cols-2 gap-3 pb-3 mb-3 border-b border-sand">
        <div>
          <p class="text-[10px] text-slate mb-0.5">Zona más afectada</p>
          <p class="text-[12px] font-bold text-ink">${worstName}</p>
          ${worstPct != null ? `<p class="text-[11px] text-slate">${worstPct}%</p>` : ''}
        </div>
        <div>
          <p class="text-[10px] text-slate mb-0.5">Zona menos afectada</p>
          <p class="text-[12px] font-bold text-ink">${bestName}</p>
          ${bestPct != null ? `<p class="text-[11px] text-slate">${bestPct}%</p>` : ''}
        </div>
      </div>
      <button onclick="openDetail(${a.id})"
        class="w-full bg-forest text-white text-[12px] font-semibold py-3 rounded-xl flex items-center justify-center gap-2 hover:bg-forest/90 transition-colors">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        Ver análisis
      </button>
    </div>`
}

function _histFilterBar(analyses) {
  const conds    = [...new Set(analyses.map(a => a.top1_label).filter(Boolean))]
  const condOpts = conds.map(c => `<option value="${c}">${_LABEL_ES[c] || c}</option>`).join('')
  const periodOpts = `
    <option value="30">Últimos 30 días</option>
    <option value="90">Últimos 3 meses</option>
    <option value="180">Últimos 6 meses</option>
    <option value="365">Último año</option>`
  const searchIcon = `<svg class="w-3.5 h-3.5 text-slate pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`

  return `
    <div class="hidden lg:flex items-center gap-3 mb-5">
      <div class="relative">
        <span class="absolute left-3 top-1/2 -translate-y-1/2">${searchIcon}</span>
        <input id="hist-search" type="text" placeholder="Buscar análisis"
          class="text-[12px] border border-sand rounded-full pl-9 pr-4 py-2 w-52 bg-white text-ink placeholder:text-slate/50 outline-none focus:border-forest/40 transition-colors" />
      </div>
      <select id="hist-cond" class="text-[12px] border border-sand rounded-full px-4 py-2 bg-white text-ink outline-none focus:border-forest/40 cursor-pointer">
        <option value="">Todos los análisis</option>${condOpts}
      </select>
      <select id="hist-period" class="text-[12px] border border-sand rounded-full px-4 py-2 bg-white text-ink outline-none focus:border-forest/40 cursor-pointer">
        <option value="">Todos los períodos</option>${periodOpts}
      </select>
    </div>
    <div class="flex lg:hidden items-center gap-2 mb-4">
      <div class="relative flex-1">
        <span class="absolute left-3 top-1/2 -translate-y-1/2">${searchIcon}</span>
        <input id="hist-search-m" type="text" placeholder="Buscar"
          class="w-full text-[12px] border border-sand rounded-xl pl-9 pr-3 py-2 bg-white text-ink placeholder:text-slate/50 outline-none focus:border-forest/40 transition-colors" />
      </div>
      <select id="hist-cond-m" class="text-[12px] border border-sand rounded-xl px-3 py-2 bg-white text-ink outline-none cursor-pointer flex-shrink-0">
        <option value="">Todos</option>${condOpts}
      </select>
      <select id="hist-period-m" class="text-[12px] border border-sand rounded-xl px-3 py-2 bg-white text-ink outline-none cursor-pointer flex-shrink-0">
        <option value="">Filtros</option>${periodOpts}
      </select>
    </div>`
}

function _populateHistoryTab(analyses) {
  const container = document.getElementById('hist-items')
  if (!container) return

  _analysisUserNum = {}
  analyses.forEach((a, i) => { _analysisUserNum[a.id] = analyses.length - i })

  if (!analyses.length) {
    container.innerHTML = `
      <h2 class="text-[17px] font-bold text-ink">Historial de análisis</h2>
      <p class="text-[11px] text-slate mt-0.5 mb-4">Consulta tus análisis anteriores y observa tu progreso.</p>
      <div class="card card-body text-center py-10">
        <p class="text-xs text-slate">No tienes análisis registrados aún.</p>
        <button class="btn-primary mt-4 max-w-xs mx-auto" data-go="capture">Hacer primer análisis</button>
      </div>`
    return
  }

  container.innerHTML = `
    <h2 class="text-[17px] font-bold text-ink">Historial de análisis</h2>
    <p class="text-[11px] text-slate mt-0.5 mb-5">Consulta tus análisis anteriores y observa tu progreso.</p>

    ${_histFilterBar(analyses)}

    <div class="hidden lg:block overflow-x-auto rounded-2xl border border-sand bg-white mb-4">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-sand/40 border-b border-sand">
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">#</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Condición</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Severidad</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Zona más afectada</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Zona menos afectada</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Estado</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Fecha</th>
            <th class="px-4 py-3 text-[10px] font-semibold text-slate uppercase tracking-wider">Acción</th>
          </tr>
        </thead>
        <tbody id="hist-tbody">
          ${analyses.map(a => _histTableRow(a)).join('')}
        </tbody>
      </table>
    </div>

    <div id="hist-cards" class="lg:hidden space-y-3 mb-4">
      ${analyses.map(a => _histCard(a)).join('')}
    </div>

    <div class="flex items-center gap-x-5 gap-y-2 flex-wrap pt-3 border-t border-sand/60">
      <span class="text-[11px] font-semibold text-ink">Niveles de severidad</span>
      <span class="flex items-center gap-1.5 text-[11px] text-slate"><span class="w-2.5 h-2.5 rounded-full bg-ok inline-block flex-shrink-0"></span>Leve (0-20%)</span>
      <span class="flex items-center gap-1.5 text-[11px] text-slate"><span class="w-2.5 h-2.5 rounded-full bg-warn inline-block flex-shrink-0"></span>Moderado (21-50%)</span>
      <span class="flex items-center gap-1.5 text-[11px] text-slate"><span class="w-2.5 h-2.5 rounded-full bg-[#E8906A] inline-block flex-shrink-0"></span>Alto (51-75%)</span>
      <span class="flex items-center gap-1.5 text-[11px] text-slate"><span class="w-2.5 h-2.5 rounded-full bg-rose inline-block flex-shrink-0"></span>Severo (76-100%)</span>
    </div>
    <p class="hist-count text-[10px] text-slate text-center mt-3">Mostrando ${analyses.length} de ${analyses.length} análisis</p>`

  _attachHistoryFilters(analyses)
}

function _attachHistoryFilters(allAnalyses) {
  function applyFilters() {
    const search = (
      document.getElementById('hist-search')?.value ||
      document.getElementById('hist-search-m')?.value || ''
    ).toLowerCase().trim()
    const cond   = document.getElementById('hist-cond')?.value     || document.getElementById('hist-cond-m')?.value   || ''
    const period = document.getElementById('hist-period')?.value   || document.getElementById('hist-period-m')?.value || ''
    const cutoff = period ? Date.now() - parseInt(period) * 86400000 : null

    const filtered = allAnalyses.filter(a => {
      if (search && !(_LABEL_ES[a.top1_label] || '').toLowerCase().includes(search)) return false
      if (cond   && a.top1_label !== cond) return false
      if (cutoff && new Date(a.created_at).getTime() < cutoff) return false
      return true
    })

    const tbody = document.getElementById('hist-tbody')
    if (tbody) tbody.innerHTML = filtered.length
      ? filtered.map(a => _histTableRow(a)).join('')
      : `<tr><td colspan="8" class="py-8 text-center text-xs text-slate">No hay análisis que coincidan.</td></tr>`

    const cards = document.getElementById('hist-cards')
    if (cards) cards.innerHTML = filtered.length
      ? filtered.map(a => _histCard(a)).join('')
      : `<p class="text-center text-xs text-slate py-8">No hay análisis que coincidan.</p>`

    const counter = document.querySelector('.hist-count')
    if (counter) counter.textContent = `Mostrando ${filtered.length} de ${allAnalyses.length} análisis`
  }

  ;['hist-search', 'hist-cond', 'hist-period', 'hist-search-m', 'hist-cond-m', 'hist-period-m'].forEach(id => {
    const el = document.getElementById(id)
    if (!el) return
    el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', applyFilters)
  })
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

  // ── 4. Zonas principales + subzonas anidadas (colapsadas) ───────────────
  let zonesDisplayHTML = ''
  const zonesDisp = r.zones_display    || {}
  const zonesDiag = r.zones_diagnostic || {}
  if (Object.keys(zonesDisp).length) {
    zonesDisplayHTML = `
      <div class="mb-3">
        <p class="text-[9px] text-slate uppercase tracking-widest font-semibold mb-2">
          Zonas principales
        </p>
        <div class="space-y-2">
          ${Object.entries(zonesDisp).map(([zona, m]) => {
            const name     = _ZONE_ES[zona] || zona
            const zSev     = Math.round(m.severity * 100)
            const eritPct  = Math.round((m.erythema  ?? 0) * 100)
            const comPct   = Math.round((m.comedones ?? 0) * 100)
            const scaPct   = Math.round((m.scaling ?? m.descamacion ?? 0) * 100)
            const children = (_ZONE_CHILDREN[zona] || []).filter(k => zonesDiag[k])
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
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">eritema ${eritPct}%</span>
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">comedones ${comPct}%</span>
                  <span class="text-[9px] bg-white/80 rounded-full px-2 py-0.5 text-slate">escamas ${scaPct}%</span>
                </div>
                ${children.length ? `
                <div class="border-t border-sand/60 mt-2.5 pt-2">
                  <button onclick="toggleZoneSub('${zona}')" id="zone-sub-${zona}-btn"
                    class="flex items-center gap-1 text-[9px] font-medium text-slate hover:text-ink transition-colors w-full">
                    ${_chevron(false)} Ver subzonas (${children.length})
                  </button>
                  <div id="zone-sub-${zona}" class="hidden mt-2 space-y-1.5">
                    ${children.map(subKey => {
                      const s       = zonesDiag[subKey]
                      const subName = _ZONE_ES[subKey] || subKey
                      const sSev    = Math.round(s.severity * 100)
                      const sErit   = Math.round((s.erythema  ?? 0) * 100)
                      const sCom    = Math.round((s.comedones ?? 0) * 100)
                      return `
                        <div class="bg-white/60 rounded-lg px-2.5 py-2">
                          <div class="flex justify-between items-center mb-1">
                            <span class="text-[10px] font-medium text-ink">${subName}</span>
                            <span class="text-[10px] font-bold ${_sevText(s.severity)}">${sSev}%</span>
                          </div>
                          <div class="w-full bg-sand/60 rounded-full h-1 mb-1.5">
                            <div class="${_sevBg(s.severity)} h-1 rounded-full" style="width:${sSev}%"></div>
                          </div>
                          <div class="flex gap-1 flex-wrap">
                            <span class="text-[8px] bg-white/70 rounded-full px-1.5 py-0.5 text-slate/70">er ${sErit}%</span>
                            <span class="text-[8px] bg-white/70 rounded-full px-1.5 py-0.5 text-slate/70">co ${sCom}%</span>
                          </div>
                        </div>`
                    }).join('')}
                  </div>
                </div>` : ''}
              </div>`
          }).join('')}
        </div>
      </div>`
  }

  return `${diagHTML}${statsHTML}${topNHTML}${zonesDisplayHTML}`
}

// ── RECOMENDACIONES DE PRODUCTOS ──────────────────────────────────────────────

function _scoreInfo(score) {
  if (score >= 70) return { label: 'Alta relevancia', bg: 'bg-forest/10', color: 'text-forest' }
  if (score >= 55) return { label: 'Buena',           bg: 'bg-ok/10',     color: 'text-ok'     }
  return                  { label: 'Compatible',      bg: 'bg-sand/60',   color: 'text-slate'  }
}

function _productRow(p, rank, borderTop) {
  const matched = p.matched_ingredients || []
  const si      = _scoreInfo(p.score || 0)
  return `
    <div class="flex items-start gap-2.5 py-2.5 ${borderTop ? 'border-t border-sand/60' : ''}">
      <span class="text-[10px] font-bold text-slate/25 w-3.5 flex-shrink-0 pt-0.5">${rank}</span>
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-1.5 mb-0.5">
          <p class="text-[11px] font-semibold text-ink leading-snug">${p.name || '—'}</p>
          <span class="text-[8px] font-semibold ${si.bg} ${si.color} rounded-full px-2 py-0.5 flex-shrink-0 whitespace-nowrap">${si.label}</span>
        </div>
        <p class="text-[10px] text-slate">${p.brand || '—'}</p>
        ${matched.length
          ? `<div class="flex flex-wrap gap-1 mt-1.5">
               ${matched.map(m => `<span class="text-[8px] bg-ok/10 text-ok font-medium rounded-full px-2 py-0.5">&#10003; ${m}</span>`).join('')}
             </div>`
          : `<p class="text-[8px] text-slate/40 mt-1 italic">Compatible &mdash; sin activos específicos</p>`}
      </div>
    </div>`
}

function _chevron(up) {
  const d = up ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'
  return `<svg class="w-3 h-3 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="${d}"/></svg>`
}

function _renderRecoPanel(data, condIdx) {
  const conditions = data.conditions || []
  if (!conditions.length) {
    return '<p class="text-[11px] text-slate text-center py-4">Sin recomendaciones disponibles.</p>'
  }

  const cond = conditions[condIdx] || conditions[0]
  const CATS = ['cleanser', 'moisturizer', 'spf', 'serum']

  const tabsHTML = conditions.length > 1 ? `
    <div class="flex flex-wrap gap-2 mb-4">
      ${conditions.map((c, i) => {
        const name   = _LABEL_ES[c.condition] || c.condition
        const pct    = Math.round((c.confidence || 0) * 100)
        const active = i === condIdx
        return `<button onclick="selectRecoCondition(${i})"
          class="flex items-center gap-1.5 text-[11px] font-medium px-3 py-1.5 rounded-full transition-colors
                 ${active ? 'bg-forest text-white font-semibold shadow-sm' : 'bg-sand/70 text-slate hover:bg-sand'}">
          ${name}
          <span class="text-[9px] rounded-full px-1.5 py-0.5
                       ${active ? 'bg-white/25 text-white' : 'bg-sand text-slate/60'}">${pct}%</span>
        </button>`
      }).join('')}
    </div>` : ''

  const reco        = cond.recommendations || {}
  const visibleCats = CATS.filter(cat => reco[cat]?.length)

  if (!visibleCats.length) {
    return `${tabsHTML}<p class="text-[11px] text-slate text-center py-4">Sin productos disponibles para esta condición en el catálogo.</p>`
  }

  const hasMultiple = visibleCats.some(cat => (reco[cat] || []).length > 1)
  const globalBar   = hasMultiple ? `
    <div class="flex justify-end mb-3">
      <button onclick="toggleAllReco()" id="reco-global-toggle"
        class="flex items-center gap-1 text-[9px] font-medium text-forest hover:opacity-75 transition-opacity">
        ${_chevron(false)} Expandir todo
      </button>
    </div>` : ''

  const catsHTML = visibleCats.map(cat => {
    const products = reco[cat]
    const catES    = _CATEGORY_ES[cat] || cat
    const catDsc   = _CAT_DESC[cat]   || ''
    const catId    = `reco-cat-${cat}`
    const extra    = products.length - 1

    return `
      <div class="mb-3 last:mb-0">
        <div class="flex items-center justify-between mb-1.5 px-1">
          <div class="flex items-center gap-2 min-w-0">
            <p class="text-[10px] font-bold text-ink uppercase tracking-wide">${catES}</p>
            <p class="text-[9px] text-slate/50 truncate">${catDsc}</p>
          </div>
          ${extra > 0 ? `
          <button onclick="toggleReco('${catId}')" id="${catId}-btn"
            data-total="${extra}"
            class="flex items-center gap-1 text-[9px] font-medium text-forest hover:opacity-75 transition-opacity flex-shrink-0 ml-2">
            ${_chevron(false)} Ver ${extra} más
          </button>` : ''}
        </div>
        <div class="bg-sand/30 rounded-xl px-3 py-1">
          ${_productRow(products[0], 1, false)}
          ${extra > 0 ? `
          <div id="${catId}-more" class="hidden">
            ${products.slice(1).map((p, i) => _productRow(p, i + 2, true)).join('')}
          </div>` : ''}
        </div>
      </div>`
  }).join('')

  return `${tabsHTML}${globalBar}${catsHTML}`
}

export function toggleReco(catId) {
  const more = document.getElementById(catId + '-more')
  const btn  = document.getElementById(catId + '-btn')
  if (!more || !btn) return

  const expanding = more.classList.contains('hidden')
  more.classList.toggle('hidden')
  btn.innerHTML = expanding
    ? `${_chevron(true)} Mostrar menos`
    : `${_chevron(false)} Ver ${btn.dataset.total} más`

  const allMore   = document.querySelectorAll('[id^="reco-cat-"][id$="-more"]')
  const anyHidden = [...allMore].some(el => el.classList.contains('hidden'))
  const g = document.getElementById('reco-global-toggle')
  if (g) g.innerHTML = anyHidden
    ? `${_chevron(false)} Expandir todo`
    : `${_chevron(true)} Colapsar todo`
}
window.toggleReco = toggleReco

export function toggleAllReco() {
  const allMore = document.querySelectorAll('[id^="reco-cat-"][id$="-more"]')
  if (!allMore.length) return

  const anyHidden = [...allMore].some(el => el.classList.contains('hidden'))

  allMore.forEach(el => {
    const catId = el.id.replace('-more', '')
    const btn   = document.getElementById(catId + '-btn')
    el.classList.toggle('hidden', !anyHidden)
    if (btn) btn.innerHTML = anyHidden
      ? `${_chevron(true)} Mostrar menos`
      : `${_chevron(false)} Ver ${btn.dataset.total} más`
  })

  const g = document.getElementById('reco-global-toggle')
  if (g) g.innerHTML = anyHidden
    ? `${_chevron(true)} Colapsar todo`
    : `${_chevron(false)} Expandir todo`
}
window.toggleAllReco = toggleAllReco

export function toggleZoneSub(zona) {
  const panel = document.getElementById(`zone-sub-${zona}`)
  const btn   = document.getElementById(`zone-sub-${zona}-btn`)
  if (!panel || !btn) return
  const expanding = panel.classList.contains('hidden')
  panel.classList.toggle('hidden')
  const count = panel.children.length
  btn.innerHTML = expanding
    ? `${_chevron(true)} Ocultar subzonas`
    : `${_chevron(false)} Ver subzonas (${count})`
}
window.toggleZoneSub = toggleZoneSub

async function _loadRecommendations(analysisId, containerId) {
  const token = localStorage.getItem('skinai_token')
  const panel = document.getElementById(containerId)
  if (!panel) return

  try {
    const res = await fetch(`${API}/products/recommendations/${analysisId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('No se pudieron cargar las recomendaciones')
    const data = await res.json()
    _recoData    = data
    _recoCondIdx = 0
    const p = document.getElementById(containerId)
    if (p) p.innerHTML = _renderRecoPanel(data, 0)
  } catch (err) {
    const p = document.getElementById(containerId)
    if (p) p.innerHTML = `<p class="text-[11px] text-slate text-center py-4">${err.message}</p>`
  }
}

export function selectRecoCondition(idx) {
  _recoCondIdx = idx
  const panel  = document.getElementById('reco-panel')
  if (panel && _recoData) panel.innerHTML = _renderRecoPanel(_recoData, idx)
}
window.selectRecoCondition = selectRecoCondition

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

    ${a.status === 'completed' ? `
    <!-- Productos recomendados -->
    <div class="card card-body mb-4">
      <div class="flex items-start justify-between mb-1">
        <p class="section-label">Productos recomendados</p>
        <span class="text-[8px] text-slate bg-sand/60 rounded-full px-2 py-0.5 font-medium flex-shrink-0 ml-2">Motor IA</span>
      </div>
      <p class="text-[11px] text-slate mb-3 leading-relaxed">
        Seleccionados por compatibilidad de ingredientes activos con tu condición detectada.
      </p>
      <div id="reco-panel">
        <div class="flex items-center justify-center gap-2 py-8 text-[11px] text-slate">
          <svg class="w-4 h-4 animate-spin flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          Cargando recomendaciones...
        </div>
      </div>
    </div>` : ''}

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

  if (a.status === 'completed') {
    _loadRecommendations(a.id, 'reco-panel')
  }
}

export function closeDetail() {
  const list   = document.getElementById('hist-list')
  const detail = document.getElementById('hist-detail')
  if (list)   list.classList.remove('hidden')
  if (detail) { detail.classList.add('hidden'); detail.innerHTML = '' }
}

// ── DASHBOARD TABS ────────────────────────────────────────────────────────

const TAB_IDS = ['dd', 'dh', 'dr']

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
