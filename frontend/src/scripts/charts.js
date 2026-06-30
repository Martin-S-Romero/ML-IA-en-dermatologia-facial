/**
 * charts.js
 * Inicializa las gráficas del dashboard con Chart.js.
 * Usa window._cutislabAnalyses (poblado por dashboard.js) para datos reales del modelo ML.
 * Se llama de forma lazy cuando el usuario activa la tab "Gráficas".
 */

const rose = '#C47060'
const bark = '#B89A72'
const grid = '#E8E2D6'

// ── Inicialización ────────────────────────────────────────────────────────────

export function initCharts() {
  if (typeof Chart === 'undefined') {
    setTimeout(initCharts, 300)
    return
  }

  const analyses = (window._cutislabAnalyses || [])
    .filter(a => a.status === 'completed' && a.result)

  if (analyses.length < 2) return

  document.getElementById('chart-block-lesiones')?.classList.remove('hidden')

  // Ordenar del más antiguo al más reciente para el eje X
  const sorted = [...analyses].reverse()

  Chart.defaults.font  = { family: "'DM Sans', sans-serif", size: 11 }
  Chart.defaults.color = '#5A6474'

  // ── 1. Severidad en el tiempo (eje Y categórico) ─────────────────────────
  const elLes = document.getElementById('chart-lesiones')
  if (elLes) {
    const catLabels = ['Sin señales', 'Muy leve', 'Leve', 'Moderada', 'Severa']
    const catColors = ['#9CA3AF', '#5FBA8B', '#D4942A', '#E8906A', '#C47060']

    const sevCat   = s => s < 0.10 ? 0 : s < 0.25 ? 1 : s < 0.50 ? 2 : s < 0.75 ? 3 : 4
    const segColor = ctx => catColors[Math.round((ctx.p0.parsed.y + ctx.p1.parsed.y) / 2)] ?? bark

    // Plugin: puntos de color en cada nivel del eje Y
    const yDotPlugin = {
      id: 'yDots',
      afterDraw(chart) {
        const yScale = chart.scales.y
        if (!yScale) return
        const c = chart.ctx
        for (let i = 0; i <= 4; i++) {
          const yPos = yScale.getPixelForValue(i)
          const xPos = yScale.right
          c.save()
          c.beginPath()
          c.arc(xPos, yPos, 4, 0, Math.PI * 2)
          c.fillStyle = catColors[i]
          c.fill()
          c.restore()
        }
      },
    }

    // Plugin: etiqueta de % encima de cada punto del dataset
    const pctLabelPlugin = {
      id: 'pctLabels',
      afterDatasetsDraw(chart) {
        const { ctx, scales: { x, y }, data } = chart
        const ds  = data.datasets[0]
        const raw = data._raw
        if (!ds || !raw) return
        ds.data.forEach((val, i) => {
          const score = raw[i]?.result?.severity_score ?? 0
          const pct   = Math.round(score * 100)
          const xPos  = x.getPixelForValue(i)
          const yPos  = y.getPixelForValue(val)
          const color = Array.isArray(ds.pointBackgroundColor)
            ? ds.pointBackgroundColor[i]
            : ds.pointBackgroundColor
          ctx.save()
          ctx.font         = 'bold 10px "DM Sans", sans-serif'
          ctx.fillStyle    = color ?? bark
          ctx.textAlign    = 'center'
          ctx.textBaseline = 'bottom'
          ctx.fillText(`${pct}%`, xPos, yPos - 12)
          ctx.restore()
        })
      },
    }

    const _buildLesionesChart = (slice) => {
      const pts  = slice.map(a => sevCat(a.result?.severity_score ?? 0))
      // Etiquetas X en dos líneas: "22 mar" / "2026"
      const lbls = slice.map(a => {
        const d = new Date(a.created_at)
        return [
          d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
          d.getFullYear().toString(),
        ]
      })
      return {
        labels: lbls,
        datasets: [{
          data: pts,
          segment: { borderColor: segColor },
          backgroundColor: rose + '20',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: pts.map(v => catColors[v]),
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8,
          borderWidth: 2.5,
        }],
      }
    }

    const lesData = _buildLesionesChart(sorted)
    lesData._raw  = sorted

    Chart.getChart(elLes)?.destroy()
    const lesChart = new Chart(elLes, {
      type: 'line',
      data: lesData,
      plugins: [yDotPlugin, pctLabelPlugin],
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { top: 24, right: 20, bottom: 4, left: 4 },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const score = ctx.chart.data._raw?.[ctx.dataIndex]?.result?.severity_score ?? 0
                return ` ${catLabels[ctx.parsed.y] ?? ''} · ${Math.round(score * 100)}%`
              },
            },
          },
        },
        scales: {
          y: {
            min: 0,
            max: 4,
            grid: { color: grid },
            border: { display: false },
            ticks: {
              stepSize: 1,
              padding: 14,
              callback: v => catLabels[v] ?? '',
            },
          },
          x: {
            grid: { display: false },
            border: { display: false },
            ticks: { maxRotation: 0, padding: 6 },
          },
        },
      },
    })

    const filterSel = document.getElementById('chart-lesiones-filter')
    if (filterSel) {
      filterSel.addEventListener('change', () => {
        const val   = filterSel.value
        const slice = val === 'all' ? sorted : sorted.slice(-Number(val))
        const d     = _buildLesionesChart(slice)
        lesChart.data.labels   = d.labels
        lesChart.data.datasets = d.datasets
        lesChart.data._raw     = slice
        lesChart.update()
      })
    }
  }

}
