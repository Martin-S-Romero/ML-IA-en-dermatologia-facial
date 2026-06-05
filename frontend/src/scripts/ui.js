/**
 * ui.js
 * Funciones de interfaz reutilizables globales:
 * drawer (hamburger), modales de términos y PDF, estados de captura.
 */

// ── DESKTOP SIDEBAR TOGGLE ────────────────────────────────────────────────
export function toggleDesktopSidebar() {
  if (window.innerWidth < 1024) return
  const sidebarWrap = document.getElementById('dashboard-sidebar')
                   || document.getElementById('account-sidebar')
  const restoreBtn  = document.getElementById('desktop-ham-restore')
  if (!sidebarWrap) return

  const isNowHidden = sidebarWrap.classList.toggle('desktop-sidebar-hidden')

  // Show/hide the restore button in the top bar
  if (restoreBtn) {
    restoreBtn.style.display = isNowHidden ? 'flex' : 'none'
  }
}

// ── DRAWER (hamburger menu) ───────────────────────────────────────────────
export function toggleDrawer() {
  const drawer  = document.getElementById('side-drawer')
  const overlay = document.getElementById('drawer-overlay')
  if (!drawer || !overlay) return

  const isOpen = drawer.classList.contains('open')
  drawer.classList.toggle('open', !isOpen)
  overlay.classList.toggle('open', !isOpen)
  // Update all hamburger buttons (multiple can exist: navbar, mobile page headers)
  document.querySelectorAll('.ham-btn').forEach(btn => {
    btn.setAttribute('aria-expanded', String(!isOpen))
    btn.classList.toggle('open', !isOpen)
  })
}

export function closeDrawer() {
  const drawer  = document.getElementById('side-drawer')
  const overlay = document.getElementById('drawer-overlay')
  if (drawer)  drawer.classList.remove('open')
  if (overlay) overlay.classList.remove('open')
  document.querySelectorAll('.ham-btn').forEach(btn => {
    btn.setAttribute('aria-expanded', 'false')
    btn.classList.remove('open')
  })
}

// ── TERMS MODAL ───────────────────────────────────────────────────────────
export function showTerms() {
  closeDrawer()
  const m = document.getElementById('terms-modal')
  if (m) { m.style.display = 'flex'; m.removeAttribute('hidden') }
}

export function hideTerms() {
  const m = document.getElementById('terms-modal')
  if (m) m.style.display = 'none'
}

// ── PDF EXPORT MODAL ──────────────────────────────────────────────────────
export function openPdfModal() {
  const m = document.getElementById('pdf-modal')
  if (!m) return
  m.style.display = 'flex'

  const form = document.getElementById('pdf-form')
  const gen  = document.getElementById('pdf-generating')
  const suc  = document.getElementById('pdf-success')
  if (form) form.style.display = 'block'
  if (gen)  gen.classList.add('hidden')
  if (suc)  suc.classList.add('hidden')
}

export function closePdfModal() {
  const m = document.getElementById('pdf-modal')
  if (m) m.style.display = 'none'
}

export function generatePdf() {
  const form = document.getElementById('pdf-form')
  const gen  = document.getElementById('pdf-generating')
  const suc  = document.getElementById('pdf-success')

  if (form) form.style.display = 'none'
  if (gen)  gen.classList.remove('hidden')

  setTimeout(() => {
    if (gen) gen.classList.add('hidden')
    if (suc) suc.classList.remove('hidden')
  }, 2200)
}

// ── CAPTURE STATES ────────────────────────────────────────────────────────
export function showCaptureError() {
  const normal = document.getElementById('capture-normal')
  const error  = document.getElementById('capture-error')
  if (normal) normal.classList.add('hidden')
  if (error)  error.classList.remove('hidden')
}

export function hideCaptureError() {
  const normal = document.getElementById('capture-normal')
  const error  = document.getElementById('capture-error')
  if (normal) normal.classList.remove('hidden')
  if (error)  error.classList.add('hidden')
}

// ── OPTION BUTTON GROUPS ──────────────────────────────────────────────────
export function bindOptionButtons() {
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-group]')
    if (!btn || btn.tagName !== 'BUTTON') return
    if (btn.classList.contains('multi')) return  // multi-select handled per-page
    const wasSelected = btn.classList.contains('selected')
    const group = btn.dataset.group
    document.querySelectorAll(`[data-group="${group}"]`).forEach(b => b.classList.remove('selected'))
    if (!wasSelected) btn.classList.add('selected')
  })
}

// ── FITZPATRICK DOTS ──────────────────────────────────────────────────────
export function bindFitzDots() {
  document.addEventListener('click', e => {
    const dot = e.target.closest('.fitz-dot')
    if (!dot) return
    const wasSelected = dot.classList.contains('selected')
    document.querySelectorAll('.fitz-dot').forEach(d => d.classList.remove('selected'))
    if (!wasSelected) dot.classList.add('selected')
  })
}
