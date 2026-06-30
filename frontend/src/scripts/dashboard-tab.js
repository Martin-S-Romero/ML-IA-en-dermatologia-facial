/**
 * dashboard-tab.js
 * Lógica del tab Dashboard (dd): estado actual, KPIs, mapa facial,
 * comparación y rutina recomendada.
 */

import {
  API,
  _LABEL_ES, _ZONE_ES, _CATEGORY_ES, _CAT_DESC,
  _formatDate, _formatDateShort, _relativeTime, _scoreInfo,
} from './dashboard-constants.js'

let _dashRecoData    = null
let _dashRecoCondIdx = 0

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

function _condColor(prob) {
  if (prob >= 0.75) return '#8B2A1A'
  if (prob >= 0.50) return '#C47060'
  if (prob >= 0.25) return '#D4942A'
  return '#2E7D5A'
}

function _updateZonesLesions(result) {
  const el = document.getElementById('dash-zones-lesions')
  if (!el) return

  const topN = result?.top_n
  if (!Array.isArray(topN) || !topN.length) {
    el.classList.add('hidden')
    return
  }

  el.innerHTML = `
    <div class="border-l border-sand pl-6 flex flex-col gap-3.5 text-[11px]">
      <p class="text-[9px] text-slate/60 uppercase tracking-widest font-semibold">Condiciones detectadas</p>
      ${topN.slice(0, 3).map((item, i) => {
        const pct   = Math.round(item.prob * 100)
        const name  = _LABEL_ES[item.label] || item.label
        const color = _condColor(item.prob)
        const isTop = i === 0
        return `
          <div class="flex items-center gap-2.5 min-w-[180px]">
            <span class="w-3 h-3 rounded-full flex-shrink-0" style="background:${color}"></span>
            <span class="${isTop ? 'font-semibold text-ink' : 'text-slate'} leading-tight flex-1">${name}</span>
            <span class="font-bold flex-shrink-0 ml-4" style="color:${color}">${pct}%</span>
          </div>`
      }).join('')}
    </div>`

  el.classList.remove('hidden')
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

function _donutSVG(pct, stroke, sizeClass = 'w-11 h-11', dark = true) {
  const trackColor = dark ? 'rgba(255,255,255,0.12)' : '#E8E2D6'
  const textColor  = dark ? 'white' : '#181C24'
  return `<svg viewBox="0 0 36 36" class="${sizeClass} mx-auto" aria-hidden="true">
    <circle cx="18" cy="18" r="15.9155" fill="none" stroke="${trackColor}" stroke-width="3"/>
    <circle cx="18" cy="18" r="15.9155" fill="none" stroke="${stroke}" stroke-width="3"
      stroke-dasharray="${pct} 100" stroke-linecap="round" transform="rotate(-90 18 18)"/>
    <text x="18" y="22" text-anchor="middle" fill="${textColor}" font-size="8" font-weight="bold"
      font-family="DM Sans,sans-serif">${pct}%</text>
  </svg>`
}

function _miniFaceSVG(worstZone) {
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

export function populateDashTab(analyses) {
  const latestEl = document.getElementById('dash-latest')
  if (!latestEl) return

  _updateFacialMap(analyses[0]?.result ?? null)
  _updateZonesLesions(analyses[0]?.result ?? null)

  const latest = analyses[0]
  if (!latest) return

  const result    = latest.result || {}
  const label     = _LABEL_ES[latest.top1_label] || 'Análisis completado'
  const conf      = latest.top1_confidence ?? 0
  const confPct   = Math.round(conf * 100)
  const sev       = result.severity_score ?? 0
  const sevPct    = Math.round(sev * 100)
  const sevInfo   = _sevLevelInfo(sev)
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
      <p class="text-[10px] text-white/75 uppercase tracking-widest font-semibold">Estado actual</p>
    </div>
    <h2 class="font-display text-xl text-cream leading-snug mb-1.5">
      Detectamos señales <span class="${sevInfo.textColor}">${sevInfo.adj}</span> de ${label}
    </h2>
    <p class="text-[12px] text-white/70 leading-relaxed mb-auto pb-2">Detectamos acné y rosácea desde una foto de tu rostro y te recomendamos una rutina con productos reales.</p>
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
      <p class="text-[11px] text-slate font-semibold uppercase tracking-widest">Severidad global</p>
      ${_donutSVG(sevPct, sevInfo.stroke, 'w-12 h-12', false)}
      <div>
        <p class="text-sm font-bold ${sevInfo.colorInk} leading-tight">${sevInfo.label}</p>
        <p class="text-xs text-slate mt-0.5">Resultado ${confPct >= 70 ? 'confiable' : 'variable'}</p>
      </div>`
    kpiSev.classList.remove('hidden')
  }

  // ── KPI: Zona más afectada ───────────────────────────────────────────────
  const kpiZone = document.getElementById('kpi-zone')
  if (kpiZone) {
    kpiZone.innerHTML = `
      <p class="text-[11px] text-slate font-semibold uppercase tracking-widest">Zona más afectada</p>
      <div class="w-10 mx-auto">${_miniFaceSVG(result.worst_zone)}</div>
      <div>
        <p class="text-sm font-bold text-rose leading-tight">${worstZone}</p>
        <p class="text-xs text-slate mt-0.5">Principales señales aquí</p>
      </div>`
    kpiZone.classList.remove('hidden')
  }

  // ── KPI: Zonas afectadas ─────────────────────────────────────────────────
  const kpiZones = document.getElementById('kpi-zones')
  if (kpiZones) {
    kpiZones.innerHTML = `
      <p class="text-[11px] text-slate font-semibold uppercase tracking-widest">Zonas afectadas</p>
      <svg class="w-8 h-8 mx-auto my-0.5" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="10" cy="10" r="5" fill="#D4942A" opacity="0.9"/>
        <circle cx="30" cy="10" r="5" fill="#D4942A" opacity="0.9"/>
        <circle cx="10" cy="30" r="5" fill="#D4942A" opacity="0.4"/>
        <circle cx="30" cy="30" r="5" fill="#D4942A" opacity="0.4"/>
        <circle cx="10" cy="20" r="5" fill="#D4942A" opacity="0.65"/>
        <circle cx="30" cy="20" r="5" fill="#D4942A" opacity="0.65"/>
      </svg>
      <div>
        <p class="text-xl font-bold text-warn leading-none">${zonesCount}<span class="text-sm text-slate/60 font-semibold">/12</span></p>
        <p class="text-xs text-slate mt-0.5">Con señales activas</p>
      </div>`
    kpiZones.classList.remove('hidden')
  }

  // ── KPI: Último análisis ─────────────────────────────────────────────────
  const kpiDate = document.getElementById('kpi-date')
  if (kpiDate) {
    kpiDate.innerHTML = `
      <p class="text-[11px] text-slate font-semibold uppercase tracking-widest">Último análisis</p>
      <svg class="w-8 h-8 mx-auto my-0.5" fill="none" stroke="#4F6FAD" stroke-width="1.6" viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
        <line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/>
        <line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <div>
        <p class="text-sm font-bold text-[#4F6FAD] leading-tight">${dateShort}</p>
        <p class="text-xs text-slate mt-0.5">${relTime}</p>
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

  const token = localStorage.getItem('cutislab_token')

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
            class="text-[11px] rounded-full px-3 py-1 font-medium transition-colors ${i === 0 ? 'bg-forest text-white' : 'bg-forest/10 text-forest hover:bg-forest/20'}">${name} · ${pct}%</button>`
        }).join('')
      : `<span class="text-[11px] text-forest bg-forest/10 rounded-full px-3 py-1 font-medium">${_LABEL_ES[conds[0].condition] || conds[0].condition} · ${Math.round((conds[0].confidence || 0) * 100)}%</span>`

    const rowsHTML = _dashRecoRows(reco)
    if (!rowsHTML) throw new Error()

    el.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <p class="section-label !mb-0">Recomendaciones basadas al último análisis</p>
        <button onclick="dtab('dh'); openDetail(${latest.id})"
          class="text-[11px] text-forest font-semibold flex items-center gap-1 bg-forest/10 hover:bg-forest/20 transition-colors px-3 py-1 rounded-full flex-shrink-0">
          Ver análisis
          <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
      <div class="flex flex-wrap gap-1 mb-1.5">
        ${condPillsHTML}
      </div>
      <div id="dash-reco-rows" class="bg-sand/30 rounded-xl px-2.5 py-0">
        ${rowsHTML}
      </div>`

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
      <div class="flex items-center gap-2 py-1 border-b border-sand/60 last:border-0">
        <span class="text-[11px] text-slate font-semibold uppercase tracking-wide w-20 flex-shrink-0">${catES}</span>
        <p class="text-xs text-ink font-medium flex-1 truncate min-w-0">${p.name}</p>
        <span class="text-[11px] font-semibold ${si.bg} ${si.color} rounded-full px-2 py-0.5 flex-shrink-0">${si.label}</span>
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
    pill.className = `text-[11px] rounded-full px-3 py-1 font-medium transition-colors ${
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

export function populateComparisonTab(analyses) {
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
    <div class="grid grid-cols-[1fr_auto_auto_auto] gap-2 pb-1.5 border-b border-sand mb-0.5">
      <span class="text-xs text-slate font-semibold">Indicador</span>
      <span class="text-xs text-slate font-semibold w-16 text-center">Anterior</span>
      <span class="text-xs text-slate font-semibold w-16 text-center">Actual</span>
      <span class="text-xs text-slate font-semibold w-14 text-right">Cambio</span>
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
      <div class="grid grid-cols-[1fr_auto_auto_auto] gap-2 items-center py-1 border-b border-sand/60 last:border-0">
        <div class="flex items-center gap-1.5 min-w-0 text-slate">
          ${r.icon}
          <span class="text-xs font-semibold text-ink truncate">${r.label}</span>
        </div>
        <div class="w-16">
          <p class="text-[11px] text-slate font-medium text-center mb-0.5">${r.prev}${r.unit}</p>
          <div class="w-full bg-sand rounded-full h-1.5">
            <div class="h-1.5 rounded-full bg-slate/40" style="width:${prevW}%"></div>
          </div>
        </div>
        <div class="w-16">
          <p class="text-[11px] text-slate font-medium text-center mb-0.5">${r.curr}${r.unit}</p>
          <div class="w-full bg-sand rounded-full h-1.5">
            <div class="h-1.5 rounded-full ${currBarClass}" style="width:${currW}%"></div>
          </div>
        </div>
        <span class="text-[11px] font-bold ${changeClass} w-14 text-right flex-shrink-0">${changeText}</span>
      </div>`
  }).join('')

  body.innerHTML = `
    <p class="text-xs text-slate font-medium mb-1.5">
      ${_formatDate(prev.created_at)} → ${_formatDate(curr.created_at)}
    </p>
    ${headerHTML}
    ${rowsHTML}
    <p class="text-xs text-slate mt-1.5">Los cambios se calculan del análisis anterior al actual.</p>`
}

// ── TAB: RUTINA ───────────────────────────────────────────────────────────

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

export function populateRoutineTab(routine) {
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
