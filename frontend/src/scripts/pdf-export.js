/**
 * pdf-export.js
 * Exportación de reportes en PDF usando window.print() sobre un iframe.
 * 3 tipos: dashboard actual, historial (completo o específico), productos recomendados.
 */

import { API, _LABEL_ES, _ZONE_ES, _ZONE_CHILDREN, _CATEGORY_ES, _formatDate } from './dashboard-constants.js'

let _pdfType = 'dashboard'

// ── MODAL CONTROL ──────────────────────────────────────────────────────────

export function openPdfModal() {
  const m = document.getElementById('pdf-modal')
  if (!m) return
  _resetModalState()
  _populateDropdown()
  m.style.display = 'flex'
}

export function closePdfModal() {
  const m = document.getElementById('pdf-modal')
  if (m) m.style.display = 'none'
}

function _resetModalState() {
  const form = document.getElementById('pdf-form')
  const gen  = document.getElementById('pdf-generating')
  if (form) form.style.display = ''
  if (gen)  gen.classList.add('hidden')
  selectPdfType('dashboard')
}

function _populateDropdown() {
  const sel = document.getElementById('pdf-analysis-select')
  if (!sel) return
  const analyses = window._cutislabAnalyses || []
  const userNum  = {}
  analyses.forEach((a, i) => { userNum[a.id] = analyses.length - i })
  const completed = analyses.filter(a => a.status === 'completed')

  sel.innerHTML = [
    '<option value="">Todos los análisis</option>',
    ...completed.map(a => {
      const n   = userNum[a.id] || '?'
      const lbl = _LABEL_ES[a.top1_label] || a.top1_label || 'Análisis'
      return `<option value="${a.id}">Análisis #${n} · ${lbl} · ${_formatDate(a.created_at)}</option>`
    }),
  ].join('')
}

export function selectPdfType(type) {
  _pdfType = type
  ;['dashboard', 'history', 'products'].forEach(t => {
    const card = document.getElementById(`pdf-type-${t}`)
    if (!card) return
    const on = t === type
    card.classList.toggle('border-forest',  on)
    card.classList.toggle('bg-forest/5',    on)
    card.classList.toggle('border-sand',   !on)
    const dot  = card.querySelector('.pdf-radio-dot')
    const ring = card.querySelector('.pdf-radio')
    if (dot)  dot.classList.toggle('hidden', !on)
    if (ring) { ring.classList.toggle('border-forest', on); ring.classList.toggle('border-sand', !on) }
  })

  const sel = document.getElementById('pdf-analysis-selector')
  const lbl = document.getElementById('pdf-selector-label')
  if (sel) sel.classList.toggle('hidden', type === 'dashboard')
  if (lbl) lbl.textContent = type === 'history'
    ? 'Seleccionar análisis (vacío = todos)'
    : 'Análisis base para las recomendaciones *'
}
window.selectPdfType = selectPdfType

// ── GENERATE (llamado desde onclick del modal) ─────────────────────────────

export async function generatePdf() {
  // Abrir la ventana SINCRÓNICAMENTE antes de cualquier await:
  // los navegadores móviles bloquean window.open() si se llama tras una operación async.
  const printWin = window.open('', '_blank', 'width=900,height=900')
  if (printWin) {
    printWin.document.write(
      '<html><head><title>Cargando...</title></head>' +
      '<body style="margin:0;display:flex;align-items:center;justify-content:center;' +
      'height:100vh;font-family:sans-serif;background:#fafaf8;color:#888;font-size:14px">' +
      '<p>Generando reporte...</p></body></html>'
    )
  }

  const form = document.getElementById('pdf-form')
  const gen  = document.getElementById('pdf-generating')
  if (form) form.style.display = 'none'
  if (gen)  gen.classList.remove('hidden')

  try {
    const token    = localStorage.getItem('cutislab_token')
    const analyses = window._cutislabAnalyses || []
    const selId    = document.getElementById('pdf-analysis-select')?.value || ''
    const profile  = await _fetchProfile(token)
    let html     = ''
    let filename = 'CutisLab.pdf'

    if (_pdfType === 'dashboard') {
      filename      = `Dashboard-${_fileDateStr()}.pdf`
      const routine = await _fetchRoutine(token)
      html          = _buildDashboardHtml(analyses, profile, routine)
    } else if (_pdfType === 'history') {
      if (selId) {
        const idx     = analyses.findIndex(x => String(x.id) === String(selId))
        const userNum = analyses.length - idx
        filename      = `Analisis#${userNum}-${_fileDateStr(analyses[idx]?.created_at)}.pdf`
      } else {
        filename = `Historial-${_fileDateStr()}.pdf`
      }
      html = await _buildHistoryHtml(analyses, profile, selId || null)
    } else {
      if (!selId) {
        if (gen)  gen.classList.add('hidden')
        if (form) form.style.display = ''
        if (printWin) printWin.close()
        alert('Selecciona un análisis específico para exportar los productos recomendados.')
        return
      }
      const idx     = analyses.findIndex(x => String(x.id) === String(selId))
      const userNum = analyses.length - idx
      filename      = `Productos-Analisis#${userNum}-${_fileDateStr(analyses[idx]?.created_at)}.pdf`
      const reco    = await _fetchReco(token, selId)
      html          = _buildProductsHtml(analyses, profile, selId, reco)
    }

    await _downloadPdf(html, filename, printWin)
    closePdfModal()
  } catch (err) {
    console.error('[pdf-export]', err)
    if (printWin && !printWin.closed) printWin.close()
    if (document.getElementById('pdf-generating')) document.getElementById('pdf-generating').classList.add('hidden')
    if (document.getElementById('pdf-form'))      document.getElementById('pdf-form').style.display = ''
  }
}

// Exportar un análisis específico directo desde la fila del historial
export async function exportAnalysisPdf(id) {
  // Abrir la ventana SINCRÓNICAMENTE antes de cualquier await — los navegadores
  // bloquean window.open() si se llama después de una operación async.
  const printWin = window.open('', '_blank', 'width=900,height=900')
  if (printWin) {
    printWin.document.write(
      '<html><head><title>Cargando...</title></head>' +
      '<body style="margin:0;display:flex;align-items:center;justify-content:center;' +
      'height:100vh;font-family:sans-serif;background:#fafaf8;color:#888;font-size:14px">' +
      '<p>Generando reporte...</p></body></html>'
    )
  }

  const token    = localStorage.getItem('cutislab_token')
  const analyses = window._cutislabAnalyses || []
  const allComp  = analyses.filter(x => x.status === 'completed')
  const idx      = allComp.findIndex(x => String(x.id) === String(id))
  const prev     = idx >= 0 && idx + 1 < allComp.length ? allComp[idx + 1] : null
  const userNum  = analyses.length - analyses.findIndex(x => String(x.id) === String(id))

  const [profile, a, reco, imgDataUrl] = await Promise.all([
    _fetchProfile(token),
    _fetchAnalysis(token, id),
    _fetchReco(token, id),
    _fetchImageBase64(token, id),
  ])
  if (!a) {
    if (printWin && !printWin.closed) printWin.close()
    return
  }
  const html     = _buildSingleAnalysisHtml(a, prev, profile, reco, userNum, imgDataUrl)
  const filename = `Analisis#${userNum}-${_fileDateStr(a.created_at)}.pdf`
  await _downloadPdf(html, filename, printWin)
}

// ── FETCH HELPERS ──────────────────────────────────────────────────────────

async function _fetchProfile(token) {
  try {
    const r = await fetch(`${API}/users/profile`, { headers: { Authorization: `Bearer ${token}` } })
    return r.ok ? r.json() : null
  } catch { return null }
}

async function _fetchRoutine(token) {
  try {
    const r = await fetch(`${API}/routines/active`, { headers: { Authorization: `Bearer ${token}` } })
    return r.ok ? r.json() : null
  } catch { return null }
}

async function _fetchReco(token, analysisId) {
  try {
    const r = await fetch(`${API}/products/recommendations/${analysisId}`, { headers: { Authorization: `Bearer ${token}` } })
    return r.ok ? r.json() : null
  } catch { return null }
}

async function _fetchAnalysis(token, id) {
  try {
    const r = await fetch(`${API}/analysis/${id}`, { headers: { Authorization: `Bearer ${token}` } })
    return r.ok ? r.json() : null
  } catch { return null }
}

async function _fetchImageBase64(token, id) {
  try {
    const r = await fetch(`${API}/analysis/${id}/image?token=${token}`)
    if (!r.ok) return null
    const blob = await r.blob()
    return new Promise(resolve => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result)
      reader.onerror  = () => resolve(null)
      reader.readAsDataURL(blob)
    })
  } catch { return null }
}

// ── PDF DOWNLOAD ──────────────────────────────────────────────────────────

// html2pdf ya no se usa — se reemplazó por window.print() sobre popup aislado

function _fileDateStr(isoDate) {
  const d = isoDate ? new Date(isoDate) : new Date()
  return d.toISOString().slice(0, 10)
}

async function _downloadPdf(html, filename, win) {
  const pageTitle = filename.replace(/\.pdf$/i, '')
  const fullHtml  = html.replace(/<title>[^<]*<\/title>/, `<title>${pageTitle}</title>`)

  if (win && !win.closed) {
    // Reemplazar la pantalla de "Generando..." con el reporte completo
    win.document.open()
    win.document.write(fullHtml)
    win.document.close()

    await new Promise(resolve => {
      win.addEventListener('load', resolve, { once: true })
      setTimeout(resolve, 1500)
    })

    win.onafterprint = () => win.close()
    win.print()
    return
  }

  // Fallback si el popup fue bloqueado: descargar como HTML
  const blob = new Blob([fullHtml], { type: 'text/html;charset=utf-8' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = pageTitle + '.html'
  document.body.appendChild(a); a.click(); document.body.removeChild(a)
  setTimeout(() => URL.revokeObjectURL(url), 3000)
}

// ── BASE PRINT CSS ─────────────────────────────────────────────────────────

const _CSS = `
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Helvetica Neue',Arial,sans-serif;color:#1a1a1a;background:#fff;font-size:12px;line-height:1.5}
.page{max-width:100%;padding:0 1cm}
.hdr{border-bottom:2.5px solid #2E7D5A;padding-bottom:12px;margin-bottom:16px}
.hdr-top{display:flex;justify-content:space-between;align-items:flex-start}
.brand{font-size:22px;font-weight:800;color:#2E7D5A;letter-spacing:-0.5px}
.rtype{font-size:11px;color:#888;margin-top:2px}
.hdr-date{font-size:10px;color:#aaa;text-align:right}
.prof{display:flex;flex-wrap:wrap;gap:16px;margin-top:8px;padding-top:8px;border-top:1px solid #eee}
.prof-item label{font-size:9px;color:#aaa;text-transform:uppercase;letter-spacing:.05em;display:block}
.prof-item span{font-size:11px;font-weight:600;color:#333}
h2{font-size:10px;font-weight:700;color:#2E7D5A;text-transform:uppercase;letter-spacing:.07em;margin:18px 0 8px;padding-bottom:4px;border-bottom:1px solid #e0ede7}
.diag-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px;margin-bottom:4px}
.dcard{background:#f5f9f6;border:1px solid #d4e8dd;border-radius:8px;padding:10px}
.dcard.main{background:#e8f5ed;border-color:#b8d9c8}
.metric-lbl{font-size:9px;color:#888;text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.metric-val{font-size:17px;font-weight:700;color:#1a1a1a;line-height:1}
.metric-sub{font-size:10px;color:#555;margin-top:3px}
.metric-cond{font-size:13px;font-weight:700;color:#1a1a1a;margin-bottom:2px}
table{width:100%;border-collapse:collapse;font-size:11px;margin-bottom:4px}
th{text-align:left;padding:5px 8px;background:#f0f4f2;font-weight:700;font-size:9px;text-transform:uppercase;letter-spacing:.04em;color:#666;border-bottom:1.5px solid #d8e8e0}
td{padding:6px 8px;border-bottom:1px solid #f0f0f0;vertical-align:middle}
tr:last-child td{border-bottom:none}
.bar{display:inline-block;width:64px;height:5px;background:#eee;border-radius:3px;vertical-align:middle;margin-left:6px;position:relative;overflow:hidden}
.bar-fg{display:block;height:100%;border-radius:3px}
.ok{color:#2E7D5A}.warn{color:#B45309}.high{color:#E8906A}.rose{color:#DC2626}
.bg-ok{background:#2E7D5A}.bg-warn{background:#B45309}.bg-high{background:#E8906A}.bg-rose{background:#DC2626}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700}
.badge-ok{background:#e8f5ed;color:#2E7D5A}
.badge-warn{background:#fef3c7;color:#B45309}
.badge-high{background:#fdecd0;color:#C2410C}
.badge-rose{background:#fee2e2;color:#DC2626}
.delta{font-size:11px;font-weight:600}
.delta-up{color:#DC2626}.delta-dn{color:#2E7D5A}.delta-eq{color:#aaa}
.chip{display:inline-block;background:#e8f5ed;color:#2E7D5A;font-size:9px;font-weight:600;padding:1px 6px;border-radius:8px;margin:1px 2px 1px 0}
.routine-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.routine-col h3{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;padding:4px 8px;border-radius:4px}
.am-head{background:#FEF3C7;color:#B45309}.pm-head{background:#e8f5ed;color:#2E7D5A}
.step{display:flex;gap:8px;padding:5px 0;border-bottom:1px solid #f5f5f5}
.step-num{width:18px;height:18px;border-radius:50%;background:#f0f0f0;font-size:9px;font-weight:700;color:#888;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.step-name{font-size:11px;font-weight:600;color:#1a1a1a}
.step-cat{font-size:9px;color:#888;margin-top:1px}
.prod-block{margin-bottom:10px;padding:8px;border:1px solid #eee;border-radius:6px}
.prod-name{font-size:12px;font-weight:600;color:#1a1a1a}
.prod-brand{font-size:10px;color:#888}
.prod-score{display:inline-block;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700;float:right}
.score-hi{background:#e8f5ed;color:#2E7D5A}.score-md{background:#f0faf5;color:#5FBA8B}.score-lo{background:#f5f5f5;color:#888}
.footer{margin-top:28px;padding-top:10px;border-top:1px solid #eee;font-size:9px;color:#bbb;text-align:center}
@media screen{html,body{height:auto;overflow-y:auto;min-height:0}}
@page{margin:1.4cm 1.8cm;size:A4}
@media print{.page{padding:0}}
`

// ── SHARED TEMPLATE PARTS ─────────────────────────────────────────────────

function _wrapHtml(bodyContent, title = 'Reporte CutisLab') {
  return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>${title}</title><style>${_CSS}</style></head><body><div class="page">${bodyContent}</div></body></html>`
}

function _header(name, reportType, dateStr) {
  return `
    <div class="hdr">
      <div class="hdr-top">
        <div>
          <div class="brand">CutisLab</div>
          <div class="rtype">${reportType}</div>
        </div>
        <div class="hdr-date">
          <div style="font-size:11px;font-weight:600;color:#555">${name}</div>
          <div>Generado el ${dateStr}</div>
        </div>
      </div>
    </div>`
}

function _profileSection(profile) {
  if (!profile) return ''
  const skinLabels = { oily:'Grasa', dry:'Seca', mixed:'Mixta', normal:'Normal', sensitive:'Sensible' }
  const fitzLabels = { I:'I', II:'II', III:'III', IV:'IV', V:'V', VI:'VI' }
  const items = []
  if (profile.skin_type)  items.push(`<div class="prof-item"><label>Tipo de piel</label><span>${skinLabels[profile.skin_type] || profile.skin_type}</span></div>`)
  if (profile.fitzpatrick) items.push(`<div class="prof-item"><label>Fitzpatrick</label><span>Tipo ${fitzLabels[profile.fitzpatrick] || profile.fitzpatrick}</span></div>`)
  if (profile.gender)     items.push(`<div class="prof-item"><label>Género</label><span>${profile.gender}</span></div>`)
  const allergies = profile.allergies || []
  if (allergies.length)   items.push(`<div class="prof-item"><label>Alergias registradas</label><span>${allergies.join(', ')}</span></div>`)
  if (profile.skin_conditions?.length) {
    items.push(`<div class="prof-item"><label>Condiciones previas</label><span>${profile.skin_conditions.join(', ')}</span></div>`)
  }
  return items.length ? `<div class="prof">${items.join('')}</div>` : ''
}

function _footer() {
  return `<div class="footer">CutisLab · Reporte generado automáticamente · No sustituye la consulta con un dermatólogo certificado</div>`
}

// ── SEVERITY HELPERS ──────────────────────────────────────────────────────

function _sevColor(v)  { return v < 0.25 ? '#2E7D5A' : v < 0.50 ? '#B45309' : v < 0.75 ? '#E8906A' : '#DC2626' }
function _sevClass(v)  { return v < 0.25 ? 'ok'      : v < 0.50 ? 'warn'    : v < 0.75 ? 'high'    : 'rose'    }
function _sevLabel(v)  { return v < 0.25 ? 'Leve'    : v < 0.50 ? 'Moderado': v < 0.75 ? 'Alto'    : 'Severo'  }
function _badgeClass(v){ return v < 0.25 ? 'badge-ok' : v < 0.50 ? 'badge-warn' : v < 0.75 ? 'badge-high' : 'badge-rose' }

function _bar(pct, color) {
  return `<span class="bar"><span class="bar-fg" style="width:${pct}%;background:${color}"></span></span>`
}

// ── ANALYSIS BLOCK ────────────────────────────────────────────────────────

function _analysisBlock(a, label) {
  const r        = a.result || {}
  const condKey  = r.condition || a.top1_label || ''
  const condName = _LABEL_ES[condKey] || condKey
  const conf     = Math.round((r.confidence ?? a.top1_confidence ?? 0) * 100)
  const sev      = r.severity_score ?? 0
  const sevPct   = Math.round(sev * 100)

  return `
    <h2>${label || 'Diagnóstico principal'}</h2>
    <div class="diag-grid">
      <div class="dcard main">
        <div class="metric-lbl">Condición detectada</div>
        <div class="metric-cond">${condName}</div>
        <div class="metric-sub">${_LABEL_ES[a.top1_label] !== condName ? (_LABEL_ES[a.top1_label] || '') : ''}</div>
      </div>
      <div class="dcard">
        <div class="metric-lbl">Severidad</div>
        <div class="metric-val" style="color:${_sevColor(sev)}">${sevPct}%</div>
        <div class="metric-sub" style="color:${_sevColor(sev)}">${_sevLabel(sev)}</div>
      </div>
      <div class="dcard">
        <div class="metric-lbl">Confianza</div>
        <div class="metric-val">${conf}%</div>
        <div class="metric-sub">del modelo</div>
      </div>
    </div>`
}

function _zonesBlock(a) {
  const r         = a.result || {}
  const zonesDisp = r.zones_display    || {}
  const zonesDiag = r.zones_diagnostic || {}
  const keys      = Object.keys(zonesDisp)
  if (!keys.length) return ''

  const childSet = new Set(keys.flatMap(z => _ZONE_CHILDREN[z] || []))
  const parents  = keys.filter(k => !childSet.has(k))
  if (!parents.length) return ''

  const rows = parents.flatMap(zona => {
    const m      = zonesDisp[zona]
    const sev    = m.severity ?? 0
    const sevPct = Math.round(sev * 100)
    const erit   = Math.round((m.erythema  ?? 0) * 100)
    const com    = Math.round((m.comedones ?? 0) * 100)
    const sca    = Math.round((m.scaling ?? m.descamacion ?? 0) * 100)

    const parentRow = `
      <tr>
        <td style="font-weight:600">${_ZONE_ES[zona] || zona}</td>
        <td><span class="${_sevClass(sev)}" style="font-weight:700">${sevPct}%</span>${_bar(sevPct, _sevColor(sev))}</td>
        <td>${erit}%</td><td>${com}%</td><td>${sca}%</td>
      </tr>`

    const children = (_ZONE_CHILDREN[zona] || []).filter(k => zonesDiag[k] || zonesDisp[k])
    const subRows  = children.map(subKey => {
      const s    = zonesDiag[subKey] || zonesDisp[subKey] || {}
      const sSev = s.severity ?? 0
      const sPct = Math.round(sSev * 100)
      const sEr  = Math.round((s.erythema  ?? 0) * 100)
      const sCo  = Math.round((s.comedones ?? 0) * 100)
      return `
        <tr style="background:#fafafa">
          <td style="padding-left:20px;color:#888;font-size:10px">↳ ${_ZONE_ES[subKey] || subKey}</td>
          <td><span class="${_sevClass(sSev)}" style="font-size:10px">${sPct}%</span>${_bar(sPct, _sevColor(sSev))}</td>
          <td style="font-size:10px;color:#888">${sEr}%</td>
          <td style="font-size:10px;color:#888">${sCo}%</td>
          <td style="font-size:10px;color:#888">—</td>
        </tr>`
    })

    return [parentRow, ...subRows]
  })

  return `
    <h2>Zonas afectadas</h2>
    <table>
      <thead><tr><th>Zona</th><th>Severidad</th><th>Eritema</th><th>Comedones</th><th>Escamas</th></tr></thead>
      <tbody>${rows.join('')}</tbody>
    </table>`
}

function _topNBlock(a) {
  const topN = (a.result || {}).top_n
  if (!topN?.length) return ''
  return `
    <h2>Condiciones evaluadas</h2>
    <table>
      <thead><tr><th>#</th><th>Condición</th><th>Probabilidad</th><th></th></tr></thead>
      <tbody>
        ${topN.map((item, i) => {
          const pct  = Math.round(item.prob * 100)
          const name = _LABEL_ES[item.label] || item.label
          const top  = i === 0
          return `<tr>
            <td style="color:#aaa;font-size:10px">${i + 1}</td>
            <td style="${top ? 'font-weight:700' : 'color:#555'}">${name}</td>
            <td style="font-weight:${top ? '700' : '400'};color:${top ? '#2E7D5A' : '#888'}">${pct}%</td>
            <td>${_bar(pct, top ? '#2E7D5A' : '#ccc')}</td>
          </tr>`
        }).join('')}
      </tbody>
    </table>`
}

function _recoBlock(reco) {
  if (!reco?.conditions?.length) return ''
  const CATS   = ['cleanser', 'moisturizer', 'spf', 'serum', 'exfoliant', 'retinoid', 'spot']
  const blocks = reco.conditions.map((cond, ci) => {
    const recom = cond.recommendations || {}
    const visib = CATS.filter(cat => recom[cat]?.length)
    if (!visib.length) return ''

    const condNote = reco.conditions.length > 1
      ? `<p style="font-size:10px;color:#888;margin-bottom:6px">${_LABEL_ES[cond.condition] || cond.condition} · ${Math.round((cond.confidence || 0) * 100)}% confianza</p>`
      : ''

    const catHtml = visib.map(cat => {
      const prods = (recom[cat] || []).slice(0, 3)
      const prodHtml = prods.map((p, pi) => {
        const score    = p.score || 0
        const scoreCls = score >= 70 ? 'score-hi' : score >= 55 ? 'score-md' : 'score-lo'
        const scoreLbl = score >= 70 ? 'Alta relevancia' : score >= 55 ? 'Buena' : 'Compatible'
        const chips    = (p.matched_ingredients || []).map(m => `<span class="chip">✓ ${m}</span>`).join('')
        return `<div class="prod-block">
          <span class="prod-score ${scoreCls}">${scoreLbl}</span>
          <div class="prod-name">${pi + 1}. ${p.name || '—'}</div>
          <div class="prod-brand">${p.brand || '—'}</div>
          ${chips ? `<div style="margin-top:4px">${chips}</div>` : ''}
        </div>`
      }).join('')
      return `<div style="margin-bottom:8px">
        <p style="font-size:10px;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px">${_CATEGORY_ES[cat] || cat}</p>
        ${prodHtml}
      </div>`
    }).join('')

    return `${ci > 0 ? '<hr style="border:none;border-top:1px solid #eee;margin:12px 0">' : ''}${condNote}${catHtml}`
  }).join('')

  return `<h2>Productos recomendados</h2>${blocks}`
}

function _singleAnalysisSection(a, prev, reco, userNum, imgDataUrl, isFirst) {
  const imgBlock = imgDataUrl ? `
    <h2>Imagen procesada</h2>
    <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:4px">
      <div style="flex-shrink:0;text-align:center">
        <img src="${imgDataUrl}" alt="Análisis #${userNum}"
          style="width:140px;border-radius:10px;border:1px solid #e0e0e0;object-fit:cover;object-position:top;display:block">
        <p style="font-size:8px;color:#bbb;margin-top:4px;max-width:140px">
          Ojos difuminados para proteger tu privacidad
        </p>
      </div>
      <p style="font-size:10px;color:#888;line-height:1.6;margin-top:4px">
        Esta imagen fue analizada por el modelo de IA para detectar condiciones cutáneas.
        El procesamiento de zonas afectadas se basa en la imagen completa del rostro.<br><br>
        <strong style="color:#555">Fecha del análisis:</strong> ${_formatDate(a.created_at)}
      </p>
    </div>` : ''

  return `
    ${isFirst ? '' : '<div style="page-break-before:always;break-before:page;height:0"></div>'}
    <div style="border-bottom:2px solid #2E7D5A;padding-bottom:8px;margin-bottom:16px${isFirst ? '' : ';margin-top:0'}">
      <div style="font-size:16px;font-weight:800;color:#2E7D5A">Análisis #${userNum}</div>
      <div style="font-size:10px;color:#aaa;margin-top:2px">${_formatDate(a.created_at)}</div>
    </div>
    ${imgBlock}
    ${_analysisBlock(a, 'Diagnóstico')}
    ${_topNBlock(a)}
    ${_zonesBlock(a)}
    ${prev ? _compBlock(a, prev) : ''}
    ${_recoBlock(reco)}
  `
}

function _buildSingleAnalysisHtml(a, prev, profile, reco, userNum, imgDataUrl) {
  const user  = _userName()
  const today = _todayStr()

  const imgBlock = imgDataUrl ? `
    <h2>Imagen procesada</h2>
    <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:4px">
      <div style="flex-shrink:0;text-align:center">
        <img src="${imgDataUrl}" alt="Análisis #${userNum}"
          style="width:140px;border-radius:10px;border:1px solid #e0e0e0;object-fit:cover;object-position:top;display:block">
        <p style="font-size:8px;color:#bbb;margin-top:4px;max-width:140px">
          Ojos difuminados para proteger tu privacidad
        </p>
      </div>
      <p style="font-size:10px;color:#888;line-height:1.6;margin-top:4px">
        Esta imagen fue analizada por el modelo de IA para detectar condiciones cutáneas.
        El procesamiento de zonas afectadas se basa en la imagen completa del rostro.<br><br>
        <strong style="color:#555">Fecha del análisis:</strong> ${_formatDate(a.created_at)}
      </p>
    </div>` : ''

  return _wrapHtml(`
    ${_header(user, `Análisis #${userNum} · ${_formatDate(a.created_at)}`, today)}
    ${_profileSection(profile)}
    ${imgBlock}
    ${_analysisBlock(a, 'Diagnóstico')}
    ${_topNBlock(a)}
    ${_zonesBlock(a)}
    ${prev ? _compBlock(a, prev) : ''}
    ${_recoBlock(reco)}
    ${_footer()}
  `, `CutisLab · Análisis #${userNum}`)
}

function _compBlock(curr, prev) {
  const rC = curr.result || {}
  const rP = prev.result || {}

  const indicators = [
    { label: 'Severidad global',     curr: Math.round((rC.severity_score ?? 0) * 100),    prev: Math.round((rP.severity_score ?? 0) * 100),    unit: '%', lowerBetter: true  },
    { label: 'Eritema promedio',     curr: Math.round((rC.avg_erythema   ?? 0) * 100),    prev: Math.round((rP.avg_erythema   ?? 0) * 100),    unit: '%', lowerBetter: true  },
    { label: 'Comedones promedio',   curr: Math.round((rC.avg_comedones  ?? 0) * 100),    prev: Math.round((rP.avg_comedones  ?? 0) * 100),    unit: '%', lowerBetter: true  },
    { label: 'Zonas activas',        curr: rC.affected_zones_count ?? 0,                  prev: rP.affected_zones_count ?? 0,                  unit: '',  lowerBetter: true  },
    { label: 'Escamación',           curr: Math.round((rC.avg_scaling    ?? 0) * 100),    prev: Math.round((rP.avg_scaling    ?? 0) * 100),    unit: '%', lowerBetter: true  },
  ]

  const rows = indicators.map(({ label, curr: c, prev: p, unit, lowerBetter }) => {
    const diff  = c - p
    const cls   = diff === 0 ? 'delta-eq' : (diff > 0 === lowerBetter ? 'delta-up' : 'delta-dn')
    const arrow = diff === 0 ? '–' : diff > 0 ? `▲ +${diff}${unit}` : `▼ ${diff}${unit}`
    const meaning = diff === 0 ? '' : diff > 0 === lowerBetter ? '(peor)' : '(mejor)'
    return `<tr>
      <td>${label}</td>
      <td style="font-weight:600">${c}${unit}</td>
      <td>${p}${unit}</td>
      <td><span class="delta ${cls}">${arrow}</span> <span style="font-size:9px;color:#aaa">${meaning}</span></td>
    </tr>`
  }).join('')

  return `
    <h2>Comparación con análisis anterior (${_formatDate(prev.created_at)})</h2>
    <table>
      <thead><tr><th>Indicador</th><th>Actual</th><th>Anterior</th><th>Variación</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`
}

function _routineBlock(routine) {
  if (!routine) return ''
  const am = (routine.steps || []).filter(s => s.time_of_day === 'am' || s.time_of_day === 'morning').sort((a, b) => a.order - b.order)
  const pm = (routine.steps || []).filter(s => s.time_of_day === 'pm' || s.time_of_day === 'evening').sort((a, b) => a.order - b.order)
  if (!am.length && !pm.length) return ''

  const stepRows = (steps) => steps.map((s, i) => `
    <div class="step">
      <div class="step-num">${i + 1}</div>
      <div>
        <div class="step-name">${s.product_name || s.name || '—'}</div>
        <div class="step-cat">${_CATEGORY_ES[s.category] || s.category || ''}</div>
      </div>
    </div>`).join('')

  return `
    <h2>Rutina activa</h2>
    <div class="routine-grid">
      <div class="routine-col">
        <h3 class="am-head">Mañana · AM</h3>
        ${am.length ? stepRows(am) : '<p style="font-size:11px;color:#aaa">Sin pasos</p>'}
      </div>
      <div class="routine-col">
        <h3 class="pm-head">Noche · PM</h3>
        ${pm.length ? stepRows(pm) : '<p style="font-size:11px;color:#aaa">Sin pasos</p>'}
      </div>
    </div>`
}

// ── BUILDER: DASHBOARD ────────────────────────────────────────────────────

function _buildDashboardHtml(analyses, profile, routine) {
  const a    = analyses.find(x => x.status === 'completed')
  const prev = analyses.filter(x => x.status === 'completed' && x !== a)[0] || null
  const user = _userName()
  const today = _todayStr()

  if (!a) {
    return _wrapHtml(`${_header(user, 'Resumen del dashboard', today)}${_profileSection(profile)}<p style="margin-top:20px;color:#888;font-size:12px;">Sin análisis completados disponibles.</p>${_footer()}`, 'CutisLab · Dashboard')
  }

  return _wrapHtml(`
    ${_header(user, 'Resumen del dashboard', today)}
    ${_profileSection(profile)}
    <p style="font-size:10px;color:#999;margin-top:6px;">Análisis del ${_formatDate(a.created_at)}</p>
    ${_analysisBlock(a, 'Diagnóstico actual')}
    ${_zonesBlock(a)}
    ${prev ? _compBlock(a, prev) : ''}
    ${_routineBlock(routine)}
    ${_footer()}
  `, 'CutisLab · Dashboard')
}

// ── BUILDER: HISTORIAL ────────────────────────────────────────────────────

async function _buildHistoryHtml(analyses, profile, specificId) {
  const user  = _userName()
  const today = _todayStr()

  if (specificId) {
    const token    = localStorage.getItem('cutislab_token')
    const allComp  = analyses.filter(x => x.status === 'completed')
    const idx      = allComp.findIndex(x => String(x.id) === String(specificId))
    const prev     = idx >= 0 && idx + 1 < allComp.length ? allComp[idx + 1] : null
    const userNum  = analyses.length - analyses.findIndex(x => String(x.id) === String(specificId))

    const [a, reco, imgDataUrl] = await Promise.all([
      _fetchAnalysis(token, specificId),
      _fetchReco(token, specificId),
      _fetchImageBase64(token, specificId),
    ])

    if (!a) {
      return _wrapHtml(`${_header(user, `Análisis #${userNum}`, today)}${_profileSection(profile)}<p style="margin-top:20px;color:#888">Análisis no encontrado.</p>${_footer()}`)
    }

    return _buildSingleAnalysisHtml(a, prev, profile, reco, userNum, imgDataUrl)
  }

  // Todos los análisis — reporte completo de cada uno, uno debajo del otro
  const token     = localStorage.getItem('cutislab_token')
  const completed = analyses.filter(x => x.status === 'completed')
  const userNumMap = {}
  analyses.forEach((a, i) => { userNumMap[a.id] = analyses.length - i })

  if (!completed.length) {
    return _wrapHtml(`${_header(user, 'Historial de análisis', today)}${_profileSection(profile)}<p style="margin-top:20px;color:#888">Sin análisis completados.</p>${_footer()}`)
  }

  const completedAsc = [...completed].reverse()

  const allData = await Promise.all(
    completedAsc.map(async (a, idx) => {
      const prev = idx > 0 ? completedAsc[idx - 1] : null
      const [fullA, reco, imgDataUrl] = await Promise.all([
        _fetchAnalysis(token, a.id),
        _fetchReco(token, a.id),
        _fetchImageBase64(token, a.id),
      ])
      return { a: fullA || a, prev, reco, userNum: userNumMap[a.id], imgDataUrl }
    })
  )

  const sections = allData.map((d, i) =>
    _singleAnalysisSection(d.a, d.prev, d.reco, d.userNum, d.imgDataUrl, i === 0)
  ).join('')

  return _wrapHtml(`
    ${_header(user, 'Historial completo de análisis', today)}
    ${_profileSection(profile)}
    <p style="font-size:10px;color:#999;margin-top:4px;margin-bottom:20px">${completed.length} análisis completados</p>
    ${sections}
    ${_footer()}
  `, 'CutisLab · Historial completo')
}

// ── BUILDER: PRODUCTOS RECOMENDADOS ───────────────────────────────────────

function _buildProductsHtml(analyses, profile, analysisId, reco) {
  const user     = _userName()
  const today    = _todayStr()
  const a        = analyses.find(x => String(x.id) === String(analysisId))
  const userNum  = analyses.length - analyses.findIndex(x => String(x.id) === String(analysisId))
  const anaLabel = a ? `${_LABEL_ES[a.top1_label] || a.top1_label} · ${_formatDate(a.created_at)}` : `Análisis #${userNum}`

  if (!reco?.conditions?.length) {
    return _wrapHtml(`
      ${_header(user, `Productos recomendados · #${userNum}`, today)}
      ${_profileSection(profile)}
      <p style="margin-top:20px;color:#888">Sin recomendaciones disponibles para este análisis.</p>
      ${_footer()}
    `)
  }

  const CATS = ['cleanser', 'moisturizer', 'spf', 'serum', 'exfoliant', 'retinoid', 'spot']

  const condBlocks = reco.conditions.map((cond, ci) => {
    const condName = _LABEL_ES[cond.condition] || cond.condition
    const conf     = Math.round((cond.confidence || 0) * 100)
    const recom    = cond.recommendations || {}
    const visib    = CATS.filter(cat => recom[cat]?.length)
    if (!visib.length) return ''

    const catBlocks = visib.map(cat => {
      const catName = _CATEGORY_ES[cat] || cat
      const prods   = (recom[cat] || []).slice(0, 3)
      const prodHtml = prods.map((p, pi) => {
        const score    = p.score || 0
        const scoreCls = score >= 70 ? 'score-hi' : score >= 55 ? 'score-md' : 'score-lo'
        const scoreLbl = score >= 70 ? 'Alta relevancia' : score >= 55 ? 'Buena' : 'Compatible'
        const chips    = (p.matched_ingredients || []).map(m => `<span class="chip">✓ ${m}</span>`).join('')
        return `
          <div class="prod-block">
            <span class="prod-score ${scoreCls}">${scoreLbl}</span>
            <div class="prod-name">${p.name || '—'}</div>
            <div class="prod-brand">${p.brand || '—'}</div>
            ${chips ? `<div style="margin-top:4px">${chips}</div>` : ''}
          </div>`
      }).join('')

      return `<div style="margin-bottom:12px"><p style="font-size:10px;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px">${catName}</p>${prodHtml}</div>`
    }).join('')

    const condHeader = reco.conditions.length > 1
      ? `<p style="font-size:12px;font-weight:700;color:#1a1a1a;margin-bottom:4px">${condName} <span style="font-size:10px;font-weight:400;color:#888">(confianza ${conf}%)</span></p>`
      : ''

    return `${condHeader}${catBlocks}`
  }).join('<hr style="border:none;border-top:1px solid #eee;margin:16px 0">')

  return _wrapHtml(`
    ${_header(user, `Productos recomendados · Análisis #${userNum}`, today)}
    ${_profileSection(profile)}
    <p style="font-size:10px;color:#999;margin-top:6px;margin-bottom:4px">${anaLabel}</p>
    <p style="font-size:10px;color:#aaa;margin-bottom:2px">Productos seleccionados por compatibilidad de ingredientes activos con la condición detectada.</p>
    <h2>Recomendaciones por categoría</h2>
    ${condBlocks}
    ${_footer()}
  `, `CutisLab · Productos #${userNum}`)
}

// ── UTILS ──────────────────────────────────────────────────────────────────

function _userName() {
  try { return JSON.parse(localStorage.getItem('cutislab_user') || '{}').full_name || 'Usuario' } catch { return 'Usuario' }
}

function _todayStr() {
  return new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}
