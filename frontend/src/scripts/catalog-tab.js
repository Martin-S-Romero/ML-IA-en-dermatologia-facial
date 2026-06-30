/**
 * catalog-tab.js
 * Lógica del tab Consulta de productos (dr): catálogo paginado,
 * filtros, ordenamiento y detalle de producto con análisis de ingredientes.
 */

import {
  API, _LABEL_ES, _CATEGORY_ES, _formatDate,
} from './dashboard-constants.js'

// ── ESTADO DEL CATÁLOGO ───────────────────────────────────────────────────

let _catalogPage       = 1
let _catalogPageSize   = 12
let _catalogQ          = ''
let _catalogCat        = ''
let _catalogAnalysisId = ''
let _catalogSortField  = 'name'
let _catalogSortDir    = 'asc'
let _catalogDebounce   = null
let _catalogTotal      = 0

let _analyses        = []
let _analysisUserNum = {}

// ── ENTRADA: llamada desde dtab() al abrir el catálogo por primera vez ────

export function initCatalogTab(analyses) {
  _analyses        = analyses
  _analysisUserNum = {}
  analyses.forEach((a, i) => { _analysisUserNum[a.id] = analyses.length - i })
  _populateCatalogAnalysisFilter()
  _loadCatalog()
}

// ── FILTRO POR ANÁLISIS ───────────────────────────────────────────────────

function _populateCatalogAnalysisFilter() {
  const sel = document.getElementById('catalog-analysis')
  if (!sel) return

  const completed = _analyses.filter(a => a.status === 'completed')
  const options   = ['<option value="">Todos los productos</option>']

  completed.forEach(a => {
    const num   = _analysisUserNum[a.id] || '?'
    const label = _LABEL_ES[a.top1_label] || a.top1_label || 'Análisis'
    const date  = _formatDate(a.created_at)
    options.push(`<option value="${a.id}">Análisis #${num} · ${label} · ${date}</option>`)
  })

  sel.innerHTML = options.join('')
  if (!completed.length) sel.disabled = true
}

// ── CARGA Y RENDERIZADO DE LA TABLA ──────────────────────────────────────

function _updateSortIcons() {
  ;['name', 'category', 'brand'].forEach(field => {
    const el = document.getElementById(`sort-icon-${field}`)
    if (!el) return
    if (_catalogSortField !== field) {
      el.textContent = '↕'
      el.className   = 'text-sm text-slate/50 group-hover:text-slate transition-colors'
    } else {
      el.textContent = _catalogSortDir === 'asc' ? '↑' : '↓'
      el.className   = 'text-base text-forest font-bold'
    }
  })
}

async function _loadCatalog() {
  const token    = localStorage.getItem('cutislab_token')
  const loading  = document.getElementById('catalog-loading')
  const table    = document.getElementById('catalog-table')
  const empty    = document.getElementById('catalog-empty')
  const tbody    = document.getElementById('catalog-tbody')
  const pag      = document.getElementById('catalog-pagination')
  const countLbl = document.getElementById('catalog-count-label')

  if (loading) loading.classList.remove('hidden')
  if (table)   table.classList.add('hidden')
  if (empty)   empty.classList.add('hidden')
  if (pag)     pag.innerHTML = ''

  const params = new URLSearchParams({
    page:      _catalogPage,
    page_size: _catalogPageSize,
    sort_by:   `${_catalogSortField}_${_catalogSortDir}`,
  })
  if (_catalogQ)          params.append('q', _catalogQ)
  if (_catalogCat)        params.append('category', _catalogCat)
  if (_catalogAnalysisId) params.append('analysis_id', _catalogAnalysisId)

  try {
    const res = await fetch(`${API}/products/catalog?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Error al cargar el catálogo')
    const data = await res.json()

    _catalogTotal = data.total

    if (loading) loading.classList.add('hidden')

    if (!data.items.length) {
      if (empty) empty.classList.remove('hidden')
      if (countLbl) countLbl.textContent = 'Sin resultados'
      return
    }

    if (countLbl) countLbl.textContent = `Mostrando ${data.total} producto${data.total !== 1 ? 's' : ''}`
    if (tbody)    tbody.innerHTML = data.items.map(_catalogRow).join('')
    if (table)    table.classList.remove('hidden')
    if (pag)      pag.innerHTML = _catalogPagHTML(data.total, data.page, data.page_size)
  } catch (err) {
    if (loading) loading.classList.add('hidden')
    if (empty) {
      empty.classList.remove('hidden')
      empty.innerHTML = `<p class="text-sm text-rose">${err.message}</p>`
    }
  }
}

function _catalogRow(p) {
  const catLabel = _CATEGORY_ES[p.category] || p.category || '--'
  const ingHtml  = p.key_ingredients.length
    ? p.key_ingredients.map(ing => `<span class="chip chip-green">✓ ${ing}</span>`).join(' ')
    : '<span class="text-[11px] text-slate">--</span>'

  const icon = _catalogIcon(p.category)

  return `
    <tr class="border-b border-sand last:border-0 hover:bg-sand/20 transition-colors">
      <td class="px-4 py-3">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-sand/50 rounded-lg flex items-center justify-center flex-shrink-0 text-slate/40">
            ${icon}
          </div>
          <div class="min-w-0">
            <button onclick="openProductDetail(${p.id})" class="text-sm font-semibold text-ink hover:text-forest transition-colors text-left leading-snug cursor-pointer">${_esc(p.name)}</button>
            <p class="text-[11px] text-slate">${_esc(p.brand || '')}</p>
          </div>
        </div>
      </td>
      <td class="px-4 py-3 text-xs text-slate hidden sm:table-cell">${catLabel}</td>
      <td class="px-4 py-3 text-xs text-slate hidden lg:table-cell">${_esc(p.brand || '--')}</td>
      <td class="px-4 py-3 hidden lg:table-cell">
        <div class="flex flex-wrap gap-1">${ingHtml}</div>
      </td>
      <td class="px-4 py-3 text-slate/40 text-sm text-right">›</td>
    </tr>`
}

function _catalogPagHTML(total, page, pageSize) {
  const totalPages = Math.ceil(total / pageSize)
  if (totalPages <= 1 && total <= pageSize) {
    return `
      <div></div>
      <div class="flex items-center gap-2 text-xs text-slate">
        Mostrar por:
        <select onchange="catalogPageSize(Number(this.value))"
          class="border border-sand rounded-md px-2 py-1 bg-white text-ink focus:outline-none focus:border-forest cursor-pointer">
          ${[12, 25, 50].map(n => `<option value="${n}" ${n === pageSize ? 'selected' : ''}>${n}</option>`).join('')}
        </select>
      </div>`
  }

  const maxVisible = 5
  let pages = []
  if (totalPages <= maxVisible + 2) {
    pages = Array.from({ length: totalPages }, (_, i) => i + 1)
  } else {
    pages = [1]
    const start = Math.max(2, page - 1)
    const end   = Math.min(totalPages - 1, page + 1)
    if (start > 2) pages.push('...')
    for (let i = start; i <= end; i++) pages.push(i)
    if (end < totalPages - 1) pages.push('...')
    pages.push(totalPages)
  }

  const btnCls = (p) => p === page
    ? 'w-8 h-8 rounded-full bg-forest text-white text-xs font-semibold flex items-center justify-center'
    : 'w-8 h-8 rounded-full bg-white border border-sand text-ink text-xs font-medium flex items-center justify-center hover:bg-cream cursor-pointer transition-colors'

  const pageHtml = pages.map(p =>
    p === '...'
      ? `<span class="text-slate text-xs px-1">…</span>`
      : `<button class="${btnCls(p)}" onclick="catalogGotoPage(${p})">${p}</button>`
  ).join('')

  const prev = page > 1
    ? `<button class="w-8 h-8 rounded-full bg-white border border-sand text-ink text-sm flex items-center justify-center hover:bg-cream cursor-pointer transition-colors" onclick="catalogGotoPage(${page - 1})">‹</button>`
    : `<span class="w-8 h-8 rounded-full bg-cream text-slate/30 text-sm flex items-center justify-center">‹</span>`

  const next = page < totalPages
    ? `<button class="w-8 h-8 rounded-full bg-white border border-sand text-ink text-sm flex items-center justify-center hover:bg-cream cursor-pointer transition-colors" onclick="catalogGotoPage(${page + 1})">›</button>`
    : `<span class="w-8 h-8 rounded-full bg-cream text-slate/30 text-sm flex items-center justify-center">›</span>`

  return `
    <div class="flex items-center gap-1.5">
      ${prev}${pageHtml}${next}
    </div>
    <div class="flex items-center gap-2 text-xs text-slate">
      Mostrar por:
      <select onchange="catalogPageSize(Number(this.value))"
        class="border border-sand rounded-md px-2 py-1 bg-white text-ink focus:outline-none focus:border-forest cursor-pointer">
        ${[12, 25, 50].map(n => `<option value="${n}" ${n === pageSize ? 'selected' : ''}>${n}</option>`).join('')}
      </select>
    </div>`
}

// ── ACCIONES DE ORDENAMIENTO Y FILTROS ───────────────────────────────────

export function catalogSortBy(field) {
  if (_catalogSortField === field) {
    _catalogSortDir = _catalogSortDir === 'asc' ? 'desc' : 'asc'
  } else {
    _catalogSortField = field
    _catalogSortDir   = 'asc'
  }
  _updateSortIcons()
  _catalogPage = 1
  _loadCatalog()
}

export function catalogSearch(val) {
  clearTimeout(_catalogDebounce)
  _catalogDebounce = setTimeout(() => {
    _catalogQ    = val.trim()
    _catalogPage = 1
    _loadCatalog()
  }, 350)
}

export function catalogFilter() {
  _catalogCat        = document.getElementById('catalog-cat')?.value      || ''
  _catalogAnalysisId = document.getElementById('catalog-analysis')?.value || ''
  _catalogPage       = 1
  _loadCatalog()
}

export function catalogGotoPage(p) {
  _catalogPage = p
  _loadCatalog()
  document.getElementById('dr')?.scrollTo({ top: 0, behavior: 'smooth' })
}

export function catalogPageSize(n) {
  _catalogPageSize = n
  _catalogPage     = 1
  _loadCatalog()
}

// ── DETALLE DE PRODUCTO ───────────────────────────────────────────────────

export async function openProductDetail(id) {
  const token  = localStorage.getItem('cutislab_token')
  const list   = document.getElementById('catalog-list')
  const detail = document.getElementById('catalog-detail')
  if (!list || !detail) return

  list.classList.add('hidden')
  detail.classList.remove('hidden')
  detail.innerHTML = `
    <button onclick="closeProductDetail()" class="btn-back-dark mb-5">← Volver al catálogo</button>
    <div class="max-w-2xl mx-auto py-8 text-center">
      <p class="text-xs text-slate animate-pulse">Cargando producto...</p>
    </div>`

  document.getElementById('dr')?.scrollTo({ top: 0, behavior: 'smooth' })

  try {
    const res = await fetch(`${API}/products/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('No se pudo cargar el producto.')
    const p = await res.json()
    _renderProductDetail(p, detail)
  } catch (err) {
    detail.innerHTML = `
      <button onclick="closeProductDetail()" class="btn-back-dark mb-5">← Volver al catálogo</button>
      <div class="max-w-2xl mx-auto card card-body text-center py-8 text-xs text-rose">${err.message}</div>`
  }
}

export function closeProductDetail() {
  const list   = document.getElementById('catalog-list')
  const detail = document.getElementById('catalog-detail')
  if (list)   list.classList.remove('hidden')
  if (detail) { detail.classList.add('hidden'); detail.innerHTML = '' }
  document.getElementById('dr')?.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── ANÁLISIS DE INGREDIENTES ──────────────────────────────────────────────

const _EU_ALLERGENS = new Set([
  'amyl cinnamal','amylcinnamyl alcohol','benzyl alcohol','benzyl benzoate',
  'benzyl cinnamate','benzyl salicylate','cinnamal','cinnamyl alcohol','citral',
  'citronellol','coumarin','eugenol','farnesol','geraniol','hexyl cinnamal',
  'hydroxycitronellal','hydroxyisohexyl 3-cyclohexene carboxaldehyde','isoeugenol',
  'lilial','linalool','methyl 2-octynoate','oakmoss extract','treemoss extract',
  'limonene','butylphenyl methylpropional','alpha-isomethyl ionone','anisyl alcohol',
])

const _PREGNANCY_AVOID = new Set([
  'retinol','retinyl palmitate','retinyl acetate','retinal','retinaldehyde',
  'adapalene','tretinoin','tazarotene','isotretinoin','granactive retinoid',
  'hydroquinone',
  'dmdm hydantoin','imidazolidinyl urea','diazolidinyl urea','quaternium-15',
  'diethyl phthalate','butyl phthalate',
])

function _parseIrrCom(val) {
  if (!val) return null
  const parts = val.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n))
  return parts.length >= 2 ? { irritancy: parts[0], comedogenicity: parts[1] } : null
}

function _ratingDots(value, max = 5) {
  const col = value <= 2 ? 'text-forest' : value === 3 ? 'text-warn' : 'text-rose'
  return Array.from({ length: max }, (_, i) =>
    `<span class="${i < value ? col : 'text-sand/60'}">●</span>`
  ).join('')
}

function _irrLabel(v) {
  return ['Sin datos','Muy baja','Baja','Moderada','Alta','Muy alta'][Math.min(v, 5)]
}

function _renderProductDetail(p, container) {
  const catLabel   = _CATEGORY_ES[p.category] || p.category || '--'
  const emoji      = _catEmoji(p.category)
  const ings       = (p.product_ingredients || []).sort((a, b) => a.position - b.position)
  const highlights = Array.isArray(p.highlights) ? p.highlights : []

  const highlightsHtml = highlights.length
    ? `<div class="flex flex-wrap gap-1.5 mb-4">
        ${highlights.map(h =>
          `<span class="chip chip-green text-[11px]">${_esc(h.replace('#', '').replace(/-/g, ' '))}</span>`
        ).join('')}
       </div>`
    : ''

  const descHtml = p.description
    ? `<div class="mb-4">
        <p class="section-label mb-1">Descripción</p>
        <p class="text-sm text-slate leading-relaxed">${_esc(p.description)}</p>
       </div>`
    : ''

  const suitableHtml = Array.isArray(p.suitable_for) && p.suitable_for.length
    ? `<div class="mb-4">
        <p class="section-label mb-1.5">Tipo de piel compatible</p>
        <div class="flex flex-wrap gap-1.5">
          ${p.suitable_for.map(s => `<span class="chip chip-blue">${_esc(s)}</span>`).join('')}
        </div>
       </div>`
    : ''

  const irrComParsed = ings.map(pi => _parseIrrCom(pi.irr_com)).filter(Boolean)
  const maxCom = irrComParsed.length ? Math.max(...irrComParsed.map(v => v.comedogenicity)) : null
  const maxIrr = irrComParsed.length ? Math.max(...irrComParsed.map(v => v.irritancy))      : null

  const allergenFound = ings
    .filter(pi => _EU_ALLERGENS.has((pi.ingredient.inci_name || '').toLowerCase().trim()))
    .map(pi => pi.ingredient.inci_name)
  const isAllergen    = allergenFound.length > 0

  const hasUnsafeIng  = ings.some(pi =>
    _PREGNANCY_AVOID.has((pi.ingredient.inci_name || '').toLowerCase().trim())
  )
  const hasSafeTag    = highlights.includes('#pregnancy-safe')
  const pregnancySafe = hasSafeTag ? true : hasUnsafeIng ? false : null

  const propRow = (label, content) =>
    `<div class="flex items-start gap-3 py-2.5 border-b border-sand last:border-0">
       <span class="text-[11px] text-slate font-semibold w-44 flex-shrink-0 pt-0.5">${label}</span>
       <div class="flex-1">${content}</div>
     </div>`

  const comRow = maxCom !== null
    ? propRow('Comedogenicidad',
        `<span class="text-sm tracking-tight">${_ratingDots(maxCom)}</span>
         <span class="text-[11px] text-slate ml-2">${_irrLabel(maxCom)} (${maxCom}/5)</span>`)
    : propRow('Comedogenicidad', `<span class="text-[11px] text-slate/50">Sin datos</span>`)

  const irrRow = maxIrr !== null
    ? propRow('Potencial de irritación',
        `<span class="text-sm tracking-tight">${_ratingDots(maxIrr)}</span>
         <span class="text-[11px] text-slate ml-2">${_irrLabel(maxIrr)} (${maxIrr}/5)</span>`)
    : propRow('Potencial de irritación', `<span class="text-[11px] text-slate/50">Sin datos</span>`)

  const allergenRow = propRow('Alérgenos EU',
    isAllergen
      ? `<span class="text-[11px] text-gold font-semibold">⚠ Contiene ${allergenFound.length} alergeno${allergenFound.length > 1 ? 's' : ''}</span>
         <div class="flex flex-wrap gap-1 mt-1.5">
           ${allergenFound.map(a => `<span class="chip chip-warn text-[10px]">${_esc(a)}</span>`).join('')}
         </div>`
      : `<span class="text-[11px] text-forest">✓ Sin alérgenos conocidos</span>`
  )

  const pregnancyRow = propRow('Embarazo',
    pregnancySafe === true
      ? `<span class="text-[11px] text-forest">✓ Compatible</span>`
      : pregnancySafe === false
        ? `<span class="text-[11px] text-rose">✗ No recomendado</span>`
        : `<span class="text-[11px] text-slate/50">Sin confirmación</span>`
  )

  const propsHtml = `
    <div class="mt-5">
      <p class="section-label mb-2">Propiedades</p>
      <div class="bg-white rounded-card border border-sand shadow-card px-4">
        ${comRow}${irrRow}${allergenRow}${pregnancyRow}
      </div>
    </div>`

  const ingsHtml = ings.length
    ? `<div class="mt-5">
        <p class="section-label mb-2">Ingredientes <span class="normal-case font-normal text-slate">(${ings.length} en total)</span></p>
        <div class="bg-white rounded-card border border-sand overflow-hidden shadow-card">
          ${ings.map(pi => _ingredientRow(pi)).join('')}
        </div>
       </div>`
    : ''

  container.innerHTML = `
    <button onclick="closeProductDetail()" class="btn-back-dark mb-5">← Volver al catálogo</button>
    <div class="max-w-2xl mx-auto">

      <div class="card card-body mb-1">
        <div class="flex items-start gap-4 mb-4">
          <div class="w-14 h-14 bg-sand/40 rounded-xl flex items-center justify-center flex-shrink-0 text-3xl">
            ${emoji}
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="font-display text-lg font-semibold text-ink leading-snug">${_esc(p.name)}</h2>
            <p class="text-sm text-slate mt-0.5">${_esc(p.brand || '--')} · ${_esc(catLabel)}</p>
          </div>
        </div>
        ${highlightsHtml}
        ${descHtml}
        ${suitableHtml}
      </div>

      ${propsHtml}
      ${ingsHtml}
    </div>`
}

function _ingredientRow(pi) {
  const rating = (pi.ingredient.rating || '').toLowerCase().replace(' ', '_')
  const chips  = {
    superstar:  `<span class="chip chip-green  text-[10px]">⭐ Superbueno</span>`,
    good_stuff: `<span class="chip chip-blue   text-[10px]">✓ Bueno</span>`,
    goodie:     `<span class="chip chip-blue   text-[10px]">✓ Bueno</span>`,
    ok:         `<span class="chip bg-sand text-slate text-[10px]">OK</span>`,
    caution:    `<span class="chip chip-warn   text-[10px]">⚠ Precaución</span>`,
    icky:       `<span class="chip chip-rose   text-[10px]">✗ Evitar</span>`,
  }
  const chip = chips[rating] || ''
  const fn   = pi.ingredient.function
    ? `<span class="text-[10px] text-slate/60 ml-1">· ${_esc(pi.ingredient.function.split(',')[0].trim())}</span>`
    : ''

  return `
    <div class="flex items-center gap-3 px-4 py-2.5 border-b border-sand last:border-0">
      <span class="text-[10px] text-slate/40 w-5 text-right flex-shrink-0">${pi.position}</span>
      <span class="text-xs font-medium text-ink flex-1 min-w-0">${_esc(pi.ingredient.inci_name)}${fn}</span>
      ${chip}
    </div>`
}

function _catEmoji(cat) {
  return { cleanser:'🧴', moisturizer:'💧', spf:'☀️', serum:'✨', exfoliant:'🌿', retinoid:'🔬', spot:'🎯', toner:'💦', eye:'👁️', mask:'🫧', oil:'🫙' }[cat] || '🧴'
}

function _catalogIcon(category) {
  const icons = {
    cleanser:    '<svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor"><path d="M9 2h6l1 4H8L9 2zm-1 5h8l1 14H7L8 7zm4 2a5 5 0 000 10A5 5 0 0012 9z"/></svg>',
    moisturizer: '<svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor"><path d="M12 2C8 7 5 11 5 15a7 7 0 0014 0c0-4-3-8-7-13z"/></svg>',
    spf:         '<svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
    serum:       '<svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor"><path d="M9 2h6v2l2 4v12a2 2 0 01-2 2H9a2 2 0 01-2-2V8l2-4V2zm3 9a3 3 0 100 6 3 3 0 000-6z"/></svg>',
    default:     '<svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor"><path d="M9 2h6v2l2 4v12a2 2 0 01-2 2H9a2 2 0 01-2-2V8l2-4V2z"/></svg>',
  }
  return icons[category] || icons.default
}

function _esc(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}
