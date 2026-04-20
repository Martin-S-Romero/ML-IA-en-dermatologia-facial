/**
 * charts.js
 * Inicializa las gráficas del dashboard con Chart.js.
 * Usa window._skinaiAnalyses (poblado por dashboard.js) para datos reales.
 * Se llama de forma lazy cuando el usuario activa la tab "Gráficas".
 */

let initialized = false

const rose   = '#C47060'
const forest = '#233D30'
const bark   = '#B89A72'
const ok     = '#2E7D5A'
const warn   = '#D4942A'
const grid   = '#E8E2D6'

export function initCharts() {
  if (initialized) return

  // Chart.js aún no cargó — reintentar
  if (typeof Chart === 'undefined') {
    setTimeout(initCharts, 300)
    return
  }

  const analyses = (window._skinaiAnalyses || []).filter(a => a.status === 'completed')

  // ── Sin suficientes datos ─────────────────────────────────────────────
  if (analyses.length < 2) {
    // El mensaje de "no data" del HTML ya está visible por defecto
    return
  }

  initialized = true

  // Ocultar mensaje "no data", mostrar bloques de gráficas
  const noDataCard = document.querySelector('#dg > div > .card.card-body.text-center')
  if (noDataCard) noDataCard.classList.add('hidden')
  ;['chart-block-lesiones', 'chart-block-radar', 'chart-block-sev', 'chart-block-bars'].forEach(id => {
    document.getElementById(id)?.classList.remove('hidden')
  })

  // Etiquetas del eje X usando fechas reales (del más antiguo al más reciente)
  const sorted = [...analyses].reverse()
  const labels = sorted.map(a =>
    new Date(a.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  )
  const n = labels.length

  Chart.defaults.font  = { family: "'DM Sans', sans-serif", size: 11 }
  Chart.defaults.color = '#5A6474'

  // ── 1. Lesiones en el tiempo ──────────────────────────────────────────
  // Valores en cero hasta que el modelo ML esté integrado (Fase 8)
  const elLes = document.getElementById('chart-lesiones')
  if (elLes) {
    new Chart(elLes, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Lesiones detectadas',
            data: Array(n).fill(0),
            borderColor: rose, backgroundColor: rose + '22',
            fill: true, tension: 0.4,
            pointBackgroundColor: rose, pointRadius: 5,
          },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Datos disponibles en Fase 8 (modelo ML)', color: warn, font: { size: 10 } },
        },
        scales: {
          y: { beginAtZero: true, grid: { color: grid } },
          x: { grid: { display: false } },
        },
      },
    })
  }

  // ── 2. Radar: primer vs último análisis ──────────────────────────────
  const elRadar = document.getElementById('chart-radar')
  if (elRadar) {
    new Chart(elRadar, {
      type: 'radar',
      data: {
        labels: ['Lesiones', 'Inflamación', 'Sebo', 'Hiperpig.', 'Poros', 'Cicatrices'],
        datasets: [
          {
            label: `Análisis #${sorted[0]?.id}`,
            data: [0, 0, 0, 0, 0, 0],
            borderColor: rose,   backgroundColor: rose + '33',   pointBackgroundColor: rose,
          },
          {
            label: `Análisis #${sorted[n - 1]?.id}`,
            data: [0, 0, 0, 0, 0, 0],
            borderColor: forest, backgroundColor: forest + '22', pointBackgroundColor: forest,
          },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: true, position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } },
          title: { display: true, text: 'Datos disponibles en Fase 8', color: warn, font: { size: 10 } },
        },
        scales: {
          r: { beginAtZero: true, max: 10, grid: { color: grid }, pointLabels: { font: { size: 10 } } },
        },
      },
    })
  }

  // ── 3. Severidad por análisis ─────────────────────────────────────────
  const elSev = document.getElementById('chart-sev')
  if (elSev) {
    new Chart(elSev, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: Array(n).fill(0),
          backgroundColor: Array(n).fill(ok + '88'),
          borderRadius: 6, borderSkipped: false,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Datos disponibles en Fase 8', color: warn, font: { size: 10 } },
        },
        scales: {
          y: { beginAtZero: true, max: 10, grid: { color: grid } },
          x: { grid: { display: false } },
        },
      },
    })
  }

  // ── 4. Indicadores de mejoría ─────────────────────────────────────────
  const elBars = document.getElementById('chart-bars')
  if (elBars) {
    new Chart(elBars, {
      type: 'bar',
      data: {
        labels: ['Sebo', 'Inflamación', 'Hiperpig.', 'Poros', 'Lesiones'],
        datasets: [{
          data: [0, 0, 0, 0, 0],
          backgroundColor: [ok, ok, ok, ok, ok],
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: { display: true, text: 'Datos disponibles en Fase 8', color: warn, font: { size: 10 } },
        },
        scales: {
          x: { grid: { color: grid }, ticks: { callback: v => v + '%' } },
          y: { grid: { display: false } },
        },
      },
    })
  }
}
