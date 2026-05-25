/**
 * router.js
 * Maneja la carga dinámica de páginas HTML desde /src/pages/
 * y el estado activo de la barra de navegación.
 */

export const PAGES = {
  landing:          '/src/pages/landing.html',
  auth:             '/src/pages/auth.html',
  profile:          '/src/pages/profile.html',
  capture:          '/src/pages/capture.html',
  'routine-check':  '/src/pages/routine-check.html',
  'routine-change': '/src/pages/routine-change.html',
  analyzing:        '/src/pages/analyzing.html',
  dashboard:        '/src/pages/dashboard.html',
  account:          '/src/pages/account.html',
}

// Páginas que requieren sesión activa
const PROTECTED = ['profile', 'capture', 'routine-check', 'routine-change', 'analyzing', 'dashboard', 'account']

// Páginas que no deben verse si ya hay sesión
const PUBLIC_ONLY = ['landing', 'auth']

let currentPage = null
let chartsReady = false

// ── AUTH HELPERS ─────────────────────────────────────────────────────────

export function getToken() {
  return localStorage.getItem('skinai_token')
}

export function setToken(token) {
  localStorage.setItem('skinai_token', token)
}

export function setUser(user) {
  localStorage.setItem('skinai_user', JSON.stringify(user))
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('skinai_user'))
  } catch {
    return null
  }
}

export function logout() {
  localStorage.removeItem('skinai_token')
  localStorage.removeItem('skinai_user')
  localStorage.removeItem('skinai_profile_complete')
  navigate('landing')
}

/**
 * Navega a una página por su clave.
 * Carga el HTML, lo inyecta en #app y ejecuta los scripts de la página.
 */
export async function navigate(pageKey) {
  if (!PAGES[pageKey]) {
    console.warn(`[router] Página desconocida: "${pageKey}"`)
    return
  }
  if (currentPage === pageKey) return

  const token = getToken()

  // Si la página requiere sesión y no hay token → redirigir a login
  if (PROTECTED.includes(pageKey) && !token) {
    await navigateToAuth('login')
    return
  }

  // Si ya hay sesión y quiere ir a landing/auth → redirigir según si completó el perfil
  if (PUBLIC_ONLY.includes(pageKey) && token) {
    if (currentPage === 'dashboard' || currentPage === 'profile') return
    const profileComplete = localStorage.getItem('skinai_profile_complete')
    await loadPage(profileComplete ? 'dashboard' : 'profile')
    return
  }

  await loadPage(pageKey)
}

async function navigateToAuth(view = 'register') {
  await loadPage('auth')
  // Mostrar la vista correcta tras cargar auth
  setTimeout(() => {
    if (typeof window.showAuthView === 'function') window.showAuthView(view)
  }, 50)
}

async function loadPage(pageKey) {
  const url = PAGES[pageKey]

  // El dashboard tiene su propio header — ocultar la navbar global para evitar duplicados
  const navbarSlot = document.getElementById('slot-navbar')
  if (navbarSlot) navbarSlot.style.display = pageKey === 'dashboard' ? 'none' : ''

  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const html = await res.text()

    const app = document.getElementById('app')
    app.innerHTML = html
    app.querySelector('section')?.classList.add('page-enter')

    currentPage = pageKey
    window.scrollTo({ top: 0, behavior: 'instant' })

    await runPageInit(pageKey)

  } catch (err) {
    console.error('[router] Error cargando página:', err)
  }
}

/** Inicialización específica por página */
async function runPageInit(pageKey) {
  switch (pageKey) {

    case 'auth':
      // Importar dinámicamente para no cargar si no se necesita
      const { initRegister, initLogin, initForgotPassword } = await import('./auth.js')
      initRegister()
      initLogin()
      initForgotPassword()
      break

    case 'profile':
      const { initProfile } = await import('./profile.js')
      initProfile()
      break

    case 'account':
      const { initAccount } = await import('./account.js')
      initAccount()
      // Llenar sidebar/drawer con datos del usuario
      fillUserUI()
      break

    case 'capture':
      const { initCapture } = await import('./capture.js')
      initCapture()
      break

    case 'analyzing':
      const { initAnalyzing } = await import('./analyzing.js')
      initAnalyzing()
      break

    case 'dashboard':
      await loadDashboardComponents()
      initDashboardTabs()
      fillUserUI()
      // Cargar datos reales desde la API
      const { initDashboard } = await import('./dashboard.js')
      await initDashboard()
      if (chartsReady) reinitCharts()
      break

    default:
      break
  }
}

/** Carga sidebar (desktop) y drawer (mobile) en el dashboard */
async function loadDashboardComponents() {
  // Sidebar for desktop
  const sidebarSlot = document.getElementById('dashboard-sidebar')
  if (sidebarSlot) {
    try {
      const res = await fetch('/src/components/sidebar.html')
      sidebarSlot.innerHTML = await res.text()
    } catch (_) {}
  }
}

/** Inicializa las pestañas del dashboard */
function initDashboardTabs() {
  // Activate first tab by default
  window.dtab('dd')
}

/** Inicializa los botones de selección (option-btn) */
export function initOptionButtons() {
  document.querySelectorAll('[data-group]').forEach(btn => {
    if (btn.tagName !== 'BUTTON') return
    btn.addEventListener('click', () => {
      const group = btn.dataset.group
      document.querySelectorAll(`[data-group="${group}"]`).forEach(b => {
        b.classList.remove('selected')
      })
      btn.classList.add('selected')
    })
  })
}

/** Inicializa los puntos Fitzpatrick */
export function initFitzpatrickDots() {
  document.querySelectorAll('.fitz-dot').forEach(dot => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.fitz-dot').forEach(d => d.classList.remove('selected'))
      dot.classList.add('selected')
    })
  })
}

/** Re-inicializa las gráficas si Chart.js ya está disponible */
function reinitCharts() {
  if (typeof window.initCharts === 'function') {
    chartsReady = false
    window.initCharts()
  }
}

export function setChartsReady(val) { chartsReady = val }

/** Rellena nombre/email en sidebar y drawer con datos del usuario en localStorage */
export function fillUserUI() {
  const user = getUser()
  if (!user) return

  const firstName = user.full_name?.split(' ')[0] || '--'

  const ids = {
    'dash-name-mobile':    firstName,
    'dash-name-desktop':   firstName,
    'drawer-greeting-name': firstName,
  }

  Object.entries(ids).forEach(([id, val]) => {
    const el = document.getElementById(id)
    if (el) el.textContent = val
  })
}
