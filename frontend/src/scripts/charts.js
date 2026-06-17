/**
 * charts.js
 * Inicializa las gráficas del dashboard con Chart.js.
 * Usa window._skinaiAnalyses (poblado por dashboard.js) para datos reales del modelo ML.
 * Se llama de forma lazy cuando el usuario activa la tab "Gráficas".
 */

let initialized = false

const rose   = '#C47060'
const forest = '#233D30'
const bark   = '#B89A72'
const ok     = '#2E7D5A'
const warn   = '#D4942A'
const grid   = '#E8E2D6'

// ── Helpers de datos ──────────────────────────────────────────────────────────

function _zoneAvg(result, key) {
  const zones = Object.values(result?.zones_display || {})
  if (!zones.length) return 0
  return zones.reduce((sum, z) => sum + (z[key] ?? 0), 0) / zones.length
}

// Devuelve los 5 indicadores [0-100] de un result para el radar
function _dims(result) {
  if (!result) return [0, 0, 0, 0, 0]
  return [
    Math.round((result.severity_score ?? 0) * 100),
    Math.round(_zoneAvg(result, 'erythema')  * 100),
    Math.round(_zoneAvg(result, 'comedones') * 100),
    Math.round(_zoneAvg(result, 'scaling')   * 100),
    Math.round(((result.affected_zones_count ?? 0) / 12) * 100),
  ]
}

function _sevColor(v) { return v < 25 ? ok : v < 50 ? warn : rose }

// ── Inicialización ────────────────────────────────────────────────────────────

export function initCharts() {
  if (initialized) return

  if (typeof Chart === 'undefined') {
    setTimeout(initCharts, 300)
    return
  }

  const analyses = (window._skinaiAnalyses || [])
    .filter(a => a.status === 'completed' && a.result)

  if (analyses.length < 2) return

  initialized = true

  const noDataCard = document.querySelector('#dg > div > .card.card-body.text-center')
  if (noDataCard) noDataCard.classList.add('hidden')
  ;['chart-block-lesiones', 'chart-block-radar', 'chart-block-sev', 'chart-block-bars'].forEach(id => {
    document.getElementById(id)?.classList.remove('hidden')
  })

  // Ordenar del más antiguo al más reciente para los ejes X
  const sorted = [...analyses].reverse()
  const labels = sorted.map(a =>
    new Date(a.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  )
  const n     = labels.length
  const first = sorted[0].result
  const last  = sorted[n - 1].result

  Chart.defaults.font  = { family: "'DM Sans', sans-serif", size: 11 }
  Chart.defaults.color = '#5A6474'

  // ── 1. Severidad en el tiempo ─────────────────────────────────────────────
  const elLes = document.getElementById('chart-lesiones')
  if (elLes) {
    const sevData = sorted.map(a => Math.round((a.result?.severity_score ?? 0) * 100))
    new Chart(elLes, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Severidad',
          data: sevData,
          borderColor: rose,
          backgroundColor: rose + '22',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: sevData.map(v => _sevColor(v)),
          pointRadius: 5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ` Severidad: ${ctx.parsed.y}%` } },
        },
        scales: {
          y: {
            beginAtZero: true, max: 100,
            grid: { color: grid },
            ticks: { callback: v => v + '%' },
          },
          x: { grid: { display: false } },
        },
      },
    })
  }

  // ── 2. Radar: primer vs último análisis ───────────────────────────────────
  const elRadar = document.getElementById('chart-radar')
  if (elRadar) {
    const firstDims = _dims(first)
    const lastDims  = _dims(last)
    new Chart(elRadar, {
      type: 'radar',
      data: {
        labels: ['Severidad', 'Eritema', 'Comedones', 'Escamas', 'Zonas'],
        datasets: [
          {
            label: `Análisis #${sorted[0]?.id}`,
            data: firstDims,
            borderColor: rose,
            backgroundColor: rose + '33',
            pointBackgroundColor: rose,
          },
          {
            label: `Análisis #${sorted[n - 1]?.id}`,
            data: lastDims,
            borderColor: forest,
            backgroundColor: forest + '22',
            pointBackgroundColor: forest,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: { boxWidth: 10, font: { size: 10 } },
          },
          tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.r}%` } },
        },
        scales: {
          r: {
            beginAtZero: true,
            max: 100,
            grid: { color: grid },
            pointLabels: { font: { size: 10 } },
            ticks: { display: false },
          },
        },
      },
    })
  }

  // ── 3. Severidad por análisis ─────────────────────────────────────────────
  const elSev = document.getElementById('chart-sev')
  if (elSev) {
    const sevData = sorted.map(a => Math.round((a.result?.severity_score ?? 0) * 100))
    new Chart(elSev, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: sevData,
          backgroundColor: sevData.map(v => _sevColor(v) + 'BB'),
          borderRadius: 6,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}%` } },
        },
        scales: {
          y: {
            beginAtZero: true, max: 100,
            grid: { color: grid },
            ticks: { callback: v => v + '%' },
          },
          x: { grid: { display: false } },
        },
      },
    })
  }

  // ── 4. Indicadores de mejoría (primer vs último) ──────────────────────────
  const elBars = document.getElementById('chart-bars')
  if (elBars) {
    const dimLabels = ['Severidad', 'Eritema', 'Comedones', 'Escamas', 'Zonas']
    const firstDims = _dims(first)
    const lastDims  = _dims(last)

    // Mejoría = reducción del indicador (positivo = mejoró, negativo = empeoró)
    const improvements = dimLabels.map((_, i) => {
      const f = firstDims[i], l = lastDims[i]
      if (f === 0 && l === 0) return 0
      if (f === 0) return -l
      return Math.round(((f - l) / f) * 100)
    })

    new Chart(elBars, {
      type: 'bar',
      data: {
        labels: dimLabels,
        datasets: [{
          data: improvements.map(Math.abs),
          backgroundColor: improvements.map(v => v >= 0 ? ok + 'BB' : rose + 'BB'),
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const v = improvements[ctx.dataIndex]
                return v > 0 ? ` ↓ mejoró ${v}%`
                     : v < 0 ? ` ↑ empeoró ${Math.abs(v)}%`
                     :          ' sin cambio'
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: grid },
            ticks: { callback: v => v + '%' },
          },
          y: { grid: { display: false } },
        },
      },
    })
  }
}
