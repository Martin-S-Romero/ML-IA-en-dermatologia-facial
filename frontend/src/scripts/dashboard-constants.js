/**
 * dashboard-constants.js
 * Constantes compartidas y helpers puros usados por los módulos del dashboard.
 */

export const API = 'http://localhost:8000/api'

export const _LABEL_ES = {
  'acne-comedonal':        'Acné comedonal',
  'acne-excoriated':       'Acné excoriado',
  'acne-inflammatory':     'Acné inflamatorio',
  'perioral-dermatitis':   'Dermatitis perioral',
  'rosacea-etr':           'Rosácea ETR',
  'rosacea-inflammatory':  'Rosácea inflamatoria',
  'healthy-skin':          'Piel saludable',
}

export const _DESCRIPCIONES = {
  'acne-comedonal':        'Acné comedonal — puntos negros/blancos, zona T',
  'acne-excoriated':       'Acné excoriado — marcas de rascado, mejillas/mentón',
  'acne-inflammatory':     'Acné inflamatorio — pústulas/nódulos, cara',
  'perioral-dermatitis':   'Dermatitis perioral — zona alrededor de la boca',
  'rosacea-etr':           'Rosácea eritematotelangiectásica — mejillas simétricas',
  'rosacea-inflammatory':  'Rosácea inflamatoria — centro facial',
  'healthy-skin':          'Piel sin lesiones detectables',
}

export const _MENSAJES_ALERTA = {
  'acne-excoriated':       'Este patrón puede beneficiarse de apoyo profesional para el manejo del hábito de rascado. Consulta a tu médico.',
  'perioral-dermatitis':   'La dermatitis perioral puede agravarse con corticosteroides tópicos. Consulta a un dermatólogo antes de aplicar cualquier tratamiento.',
  'rosacea-inflammatory':  'La rosácea inflamatoria requiere evaluación médica. Evita desencadenantes como calor, alcohol y productos con fragancia.',
}

export const _ZONE_ES = {
  frente:        'Frente',
  mejilla_izq:   'Mejilla izquierda',
  mejilla_der:   'Mejilla derecha',
  nariz:         'Nariz',
  menton:        'Mentón',
  ceja_izq:      'Ceja izquierda',
  ceja_der:      'Ceja derecha',
  nariz_lat_izq: 'Lat. nasal izq.',
  nariz_lat_der: 'Lat. nasal der.',
  mandibula_izq: 'Mandíbula izq.',
  mandibula_der: 'Mandíbula der.',
  zona_perioral: 'Zona perioral',
}

export const _ZONE_CHILDREN = {
  frente:      ['ceja_izq',      'ceja_der'],
  nariz:       ['nariz_lat_izq', 'nariz_lat_der'],
  menton:      ['zona_perioral'],
  mejilla_izq: ['mandibula_izq'],
  mejilla_der: ['mandibula_der'],
}

export const _CATEGORY_ES = {
  cleanser:    'Limpiador',
  moisturizer: 'Hidratante',
  spf:         'Protector solar',
  serum:       'Sérum',
  exfoliant:   'Exfoliante',
  retinoid:    'Retinoide',
  spot:        'Tratamiento puntual',
  toner:       'Tónico',
  eye:         'Contorno de ojos',
  mask:        'Mascarilla',
  oil:         'Aceite facial',
}

export const _CAT_DESC = {
  cleanser:    'Primer paso · mañana y noche',
  moisturizer: 'Hidratación y barrera',
  spf:         'Protección solar · cada mañana',
  serum:       'Activos concentrados',
}

export function _formatDate(isoStr) {
  if (!isoStr) return '--'
  try {
    return new Date(isoStr).toLocaleDateString('es-ES', {
      day: 'numeric', month: 'long', year: 'numeric',
    })
  } catch { return isoStr }
}

export function _formatDateShort(isoStr) {
  if (!isoStr) return '--'
  try {
    return new Date(isoStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch { return isoStr }
}

export function _relativeTime(isoStr) {
  if (!isoStr) return '--'
  const days = Math.floor((Date.now() - new Date(isoStr).getTime()) / 86400000)
  if (days === 0) return 'Hoy'
  if (days === 1) return 'Hace 1 día'
  return `Hace ${days} días`
}

export function _scoreInfo(score) {
  if (score >= 70) return { label: 'Alta relevancia', bg: 'bg-forest/10', color: 'text-forest' }
  if (score >= 55) return { label: 'Buena',           bg: 'bg-ok/10',     color: 'text-ok'     }
  return                  { label: 'Compatible',      bg: 'bg-sand/60',   color: 'text-slate'  }
}

export function _statusLabel(status) {
  return (
    { completed: 'Completado', failed: 'Error', processing: 'Procesando' }[status]
    || status
  )
}
