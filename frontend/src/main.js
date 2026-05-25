/**
 * main.js
 * Controlador principal de SkinAI.
 * - Carga componentes globales (navbar, drawer, modales)
 * - Define window.go() — navegación principal
 * - Registra todas las funciones globales necesarias por el HTML
 * - Inicia en la pantalla landing
 */

import { navigate, getToken, getUser, setToken, setUser, logout } from './scripts/router.js'
import { initRegister, initLogin, initForgotPassword } from './scripts/auth.js'
import { initProfile } from './scripts/profile.js'
import { initAccount } from './scripts/account.js'
import {
  toggleDesktopSidebar,
  toggleDrawer, closeDrawer,
  showTerms, hideTerms,
  openPdfModal, closePdfModal, generatePdf,
  showCaptureError, hideCaptureError,
  bindOptionButtons, bindFitzDots,
} from './scripts/ui.js'

import {
  dtab, sidebarNav,
  openDetail, closeDetail,
  switchRoutine, toggleAccordion,
} from './scripts/dashboard.js'

// ── LOAD GLOBAL COMPONENTS ───────────────────────────────────────────────
async function loadComponent(slotId, url) {
  try {
    const res  = await fetch(url)
    const html = await res.text()
    const slot = document.getElementById(slotId)
    if (slot) slot.innerHTML = html
  } catch (err) {
    console.error(`[main] Error cargando componente ${url}:`, err)
  }
}

async function bootstrap() {
  // 1. Load global components in parallel
  await Promise.all([
    loadComponent('slot-navbar', '/src/components/navbar.html'),
    loadComponent('slot-modals', '/src/components/modals.html'),
  ])

  // 2. Load drawer (injected into body so it overlays everything)
  const drawerRes  = await fetch('/src/components/drawer.html')
  const drawerHtml = await drawerRes.text()
  const drawerWrap = document.createElement('div')
  drawerWrap.innerHTML = drawerHtml
  document.body.appendChild(drawerWrap)

  // 3. Register ALL global functions (used by HTML onclick / data-go)
  registerGlobals()

  // 4. Register event delegation for data-go navigation
  document.addEventListener('click', e => {
    const el = e.target.closest('[data-go]')
    if (el) {
      e.preventDefault()
      window._goFull(el.dataset.go)
    }
  })

  // 5. Add global style for nav buttons and tab styles (not in Tailwind scan at build time)
  injectNavStyles()

  // 6. Bind utility interactions
  bindOptionButtons()
  bindFitzDots()

  // 7. Navigate to landing page (first screen)
  await navigate('landing')

  // 8. Flush queued go() calls
  window._goReady = true
  if (window._goQueue && window._goQueue.length) {
    window._goQueue.forEach(id => window._goFull(id))
    window._goQueue = []
  }
}

// ── GLOBAL FUNCTIONS ─────────────────────────────────────────────────────
function registerGlobals() {
  // Auth
  window.logout          = logout
  window.goAuth          = (view) => {
    navigate('auth').then(() => {
      setTimeout(() => window.showAuthView && window.showAuthView(view), 50)
    })
  }
  window.showAuthView    = (view) => {
    const register = document.getElementById('auth-register')
    const login    = document.getElementById('auth-login')
    if (!register || !login) return
    if (view === 'login') {
      register.classList.add('hidden')
      login.classList.remove('hidden')
    } else {
      login.classList.add('hidden')
      register.classList.remove('hidden')
    }
  }

  // Core navigation
  window._goFull = (id) => navigate(id)

  // Desktop sidebar
  window.toggleDesktopSidebar = toggleDesktopSidebar

  // Drawer
  window.toggleDrawer    = toggleDrawer
  window.closeDrawer     = closeDrawer

  // Modals
  window.showTerms       = showTerms
  window.hideTerms       = hideTerms
  window.openPdfModal    = openPdfModal
  window.closePdfModal   = closePdfModal
  window.generatePdf     = generatePdf

  // Account
  window.deleteAccount    = deleteAccount

  // Capture states
  window.showCaptureError = showCaptureError
  window.hideCaptureError = hideCaptureError

  // Dashboard
  window.dtab            = dtab
  window.sidebarNav      = sidebarNav
  window.openDetail      = openDetail
  window.closeDetail     = closeDetail
  window.switchRoutine   = switchRoutine
  window.toggleAccordion = toggleAccordion
}

// ── INJECT STYLES NOT COVERED BY TAILWIND SCAN ───────────────────────────
function injectNavStyles() {
  const style = document.createElement('style')
  style.textContent = `
    /* Nav bar buttons */
    .nav-btn {
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.12);
      color: #aaa;
      padding: 3px 9px;
      border-radius: 14px;
      cursor: pointer;
      font-size: 11px;
      font-family: 'DM Sans', sans-serif;
      transition: all 0.2s;
    }
    .nav-btn:hover, .nav-btn.active {
      background: #B89A72;
      color: #181C24;
      border-color: #B89A72;
    }

    /* Dashboard tab bar */
    .dtab {
      flex: 1;
      min-width: 70px;
      padding: 10px 0;
      font-size: 12px;
      font-weight: 600;
      color: rgba(255,255,255,0.36);
      text-align: center;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
      white-space: nowrap;
      background: transparent;
      border-top: none;
      border-left: none;
      border-right: none;
      font-family: 'DM Sans', sans-serif;
    }
    .dtab.active {
      color: #B89A72;
      border-bottom-color: #B89A72;
    }

    /* Dashboard tab pages */
    .dpage { display: none; }
    .dpage.active { display: block; }

    /* Zone labels on image */
    .zone-lbl {
      position: absolute;
      font-size: 9px;
      font-weight: 700;
      color: #fff;
      background: rgba(24,28,36,0.72);
      padding: 2px 5px;
      border-radius: 5px;
      white-space: nowrap;
    }

    /* Hamburger open state */
    .ham-btn.open span:nth-child(1) { transform: rotate(45deg) translate(4px, 4px); }
    .ham-btn.open span:nth-child(2) { opacity: 0; transform: scaleX(0); }
    .ham-btn.open span:nth-child(3) { transform: rotate(-45deg) translate(4px, -4px); }
  `
  document.head.appendChild(style)
}

// ── BOOT ─────────────────────────────────────────────────────────────────
bootstrap()
