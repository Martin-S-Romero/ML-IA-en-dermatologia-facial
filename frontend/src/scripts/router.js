/**
 * router.js
 * Maneja la carga dinámica de páginas HTML desde /src/pages/
 * y el estado activo de la barra de navegación.
 */

export const PAGES = {
  landing:           '/src/pages/landing.html',
  auth:              '/src/pages/auth.html',
  'reset-password':  '/src/pages/reset-password.html',
  profile:           '/src/pages/profile.html',
  capture:           '/src/pages/capture.html',
  'routine-check':   '/src/pages/routine-check.html',
  'routine-change':  '/src/pages/routine-change.html',
  analyzing:         '/src/pages/analyzing.html',
  dashboard:         '/src/pages/dashboard.html',
  account:           '/src/pages/account.html',
}

// Páginas que requieren sesión activa
const PROTECTED = ['profile', 'capture', 'routine-check', 'routine-change', 'analyzing', 'dashboard', 'account']

// Páginas que no deben verse si ya hay sesión
const PUBLIC_ONLY = ['landing', 'auth']

let currentPage = null
let chartsReady = false
let navSeq = 0

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

  // Páginas que requieren perfil completo — si no, forzar al perfil
  const REQUIRES_PROFILE = ['dashboard', 'capture', 'routine-check', 'routine-change', 'analyzing', 'account']
  if (REQUIRES_PROFILE.includes(pageKey) && token && !localStorage.getItem('skinai_profile_complete')) {
    await loadPage('profile')
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
  const mySeq = ++navSeq
  const url = PAGES[pageKey]

  // Only show the global navbar on authenticated flow pages that lack their own sidebar
  const NAVBAR_PAGES = ['profile', 'capture', 'routine-check', 'routine-change', 'analyzing']
  const navbarSlot = document.getElementById('slot-navbar')
  if (navbarSlot) navbarSlot.style.display = NAVBAR_PAGES.includes(pageKey) ? 'block' : 'none'

  // Limpiar el contenido anterior de inmediato para que no persista durante la carga
  const app = document.getElementById('app')
  if (app) app.innerHTML = ''

  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const html = await res.text()

    // Si una navegación más reciente ya empezó, descartar este resultado
    if (navSeq !== mySeq) return

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

    case 'reset-password': {
      const { initResetPassword } = await import('./auth.js')
      initResetPassword()
      break
    }

    case 'profile':
      const { initProfile } = await import('./profile.js')
      initProfile()
      break

    case 'account':
      await loadAccountComponents()
      setDrawerActive('account')
      fillUserUI()
      const { initAccount } = await import('./account.js')
      initAccount()
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
      setDrawerActive('dashboard')
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

/** Sets the active nav item in the global mobile drawer */
function setDrawerActive(pageKey) {
  const drawer = document.getElementById('side-drawer')
  if (!drawer) return
  drawer.querySelectorAll('.sidebar-nav-item').forEach(btn => btn.classList.remove('active'))
  const target = drawer.querySelector(`[data-go="${pageKey}"]`)
  if (target) target.classList.add('active')
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

/** Carga sidebar (desktop) en la página de cuenta */
async function loadAccountComponents() {
  const sidebarSlot = document.getElementById('account-sidebar')
  if (sidebarSlot) {
    try {
      const res = await fetch('/src/components/sidebar.html')
      sidebarSlot.innerHTML = await res.text()
      const dashBtn = sidebarSlot.querySelector('#sidebar-dash-btn')
      if (dashBtn) dashBtn.classList.remove('active')
      const accountBtn = sidebarSlot.querySelector('[data-go="account"]')
      if (accountBtn) accountBtn.classList.add('active')
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
