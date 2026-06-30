/**
 * dashboard.js — Coordinador del dashboard.
 * Orquesta la carga de datos y delega el renderizado a los módulos de cada tab.
 * Re-exporta las funciones que main.js necesita registrar en window.
 */

import { API } from './dashboard-constants.js'
import { populateDashTab, populateComparisonTab, populateRoutineTab } from './dashboard-tab.js'
import { populateHistoryTab } from './history-tab.js'
import { initCatalogTab } from './catalog-tab.js'

// Re-exports para que main.js no necesite cambiar sus imports
export { openDetail, closeDetail } from './history-tab.js'
export {
  catalogSearch, catalogFilter, catalogSortBy,
  catalogGotoPage, catalogPageSize,
  openProductDetail, closeProductDetail,
} from './catalog-tab.js'

// ── ESTADO COMPARTIDO ─────────────────────────────────────────────────────

let _analyses      = []
let _routine       = null
let _catalogLoaded = false

// ── INICIALIZACIÓN PRINCIPAL ──────────────────────────────────────────────

export async function initDashboard() {
  const token = localStorage.getItem('cutislab_token')
  if (!token) return

  _initFab()

  try {
    const [analyses, routine] = await Promise.all([
      _fetchHistory(token),
      _fetchRoutine(token),
    ])
    _analyses = analyses
    _routine  = routine

    populateDashTab(analyses)
    populateComparisonTab(analyses)
    populateHistoryTab(analyses)
    populateRoutineTab(routine)

    window._cutislabAnalyses = analyses
    import('./charts.js').then(m => m.initCharts())
  } catch (err) {
    console.error('[dashboard] Error al cargar datos:', err)
  }
}

function _initFab() {
  if (document.getElementById('fab-new-analysis')) return
  const fab = document.createElement('button')
  fab.id = 'fab-new-analysis'
  fab.setAttribute('data-go', 'capture')
  fab.className = 'fixed bottom-5 right-5 w-12 h-12 lg:w-14 lg:h-14 rounded-full shadow-lg hover:scale-105 active:scale-95 transition-transform overflow-hidden p-0 border-0 bg-transparent'
  fab.style.zIndex = '400'
  fab.innerHTML = '<img src="/img-resource/icon-mas.png" alt="Nuevo análisis" class="w-full h-full object-cover">'
  document.body.appendChild(fab)
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

// ── NAVEGACIÓN ENTRE TABS ────────────────────────────────────────────────

const TAB_IDS = ['dd', 'dh', 'dr']

export function dtab(name) {
  TAB_IDS.forEach(id => {
    const page = document.getElementById(id)
    const btn  = document.querySelector(`.dtab[data-tab="${id}"]`)
    if (page) page.classList.toggle('active', id === name)
    if (btn) {
      btn.classList.toggle('active', id === name)
      btn.setAttribute('aria-selected', String(id === name))
    }
  })

  // El botón del dashboard en el sidebar permanece activo en todas las sub-tabs
  const sidebarDash = document.getElementById('sidebar-dash-btn')
  if (sidebarDash) sidebarDash.classList.add('active')

  // Lazy-load del catálogo la primera vez que se abre
  if (name === 'dr' && !_catalogLoaded) {
    _catalogLoaded = true
    initCatalogTab(_analyses)
  }
}

export function sidebarNav(tabId) {
  if (!document.getElementById('page-dashboard')) {
    window._goFull && window._goFull('dashboard')
    setTimeout(() => dtab(tabId), 300)
  } else {
    dtab(tabId)
  }
}

// ── CONTROLES DE RUTINA Y ACORDEÓN ───────────────────────────────────────

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

export function toggleAccordion(id) {
  const el = document.getElementById(id)
  if (!el) return
  const isOpen = el.classList.contains('open')
  document.querySelectorAll('.accordion-card').forEach(c => c.classList.remove('open'))
  if (!isOpen) el.classList.add('open')
}
