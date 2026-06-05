#!/usr/bin/env python3
"""
analisis.py
Analiza ambos inci_results.jsonl y genera 3 reportes:
  - analisis_pantalla_inicio.md
  - analisis_entorno_prueba.md
  - analisis_comparacion.md
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).parent
FILE_A     = BASE_DIR / "pantalla inicio"  / "inci_results.jsonl"
FILE_B     = BASE_DIR / "entorno de prueba" / "inci_results.jsonl"
LABEL_A    = "pantalla inicio  (demo endpoint)"
LABEL_B    = "entorno de prueba (auth endpoint)"

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def get_keys_recursive(obj, prefix=""):
    """Devuelve todos los keypaths de un dict anidado."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f"{prefix}.{k}" if prefix else k
            keys.add(full)
            keys |= get_keys_recursive(v, full)
    elif isinstance(obj, list) and obj:
        keys |= get_keys_recursive(obj[0], prefix + "[]")
    return keys


def safe_pct(n, total):
    return f"{n:,} ({n/total*100:.1f}%)" if total else f"{n:,}"


# ---------------------------------------------------------------------------
# Carga y clasificacion
# ---------------------------------------------------------------------------

def load_jsonl(path: Path):
    records = []
    if not path.exists():
        print(f"[WARN] No existe: {path}")
        return records
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception as e:
                print(f"  [WARN] Linea {i} invalida: {e}")
    return records


def classify(records):
    """Clasifica registros y extrae metricas."""
    total      = len(records)
    con_prod   = []   # tiene data.product
    not_found  = []   # 404 legitimo
    errors     = []   # errores de scraper
    otros      = []   # respuesta rara

    error_types  = Counter()
    endpoints    = Counter()
    barcode_seen = set()
    duplicates   = 0

    for r in records:
        bc       = r.get("barcode", "")
        data     = r.get("data", {})
        endpoint = r.get("endpoint", "")

        if bc in barcode_seen:
            duplicates += 1
        barcode_seen.add(bc)

        if endpoint:
            # Normalizar endpoint (quitar el barcode del final)
            ep_norm = "/".join(endpoint.split("/")[:-1])
            endpoints[ep_norm] += 1

        if not isinstance(data, dict):
            otros.append(r)
        elif "product" in data:
            con_prod.append(r)
        elif data.get("statusCode") == 404 or data.get("error") == "Not Found":
            not_found.append(r)
        elif "error" in data:
            errors.append(r)
            error_types[data["error"]] += 1
        else:
            otros.append(r)

    return {
        "total"      : total,
        "con_prod"   : con_prod,
        "not_found"  : not_found,
        "errors"     : errors,
        "otros"      : otros,
        "error_types": error_types,
        "endpoints"  : endpoints,
        "barcodes"   : barcode_seen,
        "duplicates" : duplicates,
    }


# ---------------------------------------------------------------------------
# Analisis de estructura
# ---------------------------------------------------------------------------

def analyze_structure(con_prod):
    """Analiza campos presentes en registros exitosos."""
    if not con_prod:
        return {}, {}, {}

    # Frecuencia de keypaths
    keypath_counts = Counter()
    sample_size    = min(len(con_prod), 500)

    for r in con_prod[:sample_size]:
        data = r.get("data") or {}
        for kp in get_keys_recursive(data):
            keypath_counts[kp] += 1

    pct = {k: v / sample_size * 100 for k, v in keypath_counts.items()}

    # Campos de product
    product_fields = Counter()
    for r in con_prod[:sample_size]:
        prod = (r.get("data") or {}).get("product") or {}
        if isinstance(prod, dict):
            for k in prod:
                product_fields[k] += 1

    # Campos de analysis
    analysis_fields = Counter()
    for r in con_prod[:sample_size]:
        details  = (r.get("data") or {}).get("details") or {}
        analysis = details.get("analysis") or {}
        if isinstance(analysis, dict):
            for k in analysis:
                analysis_fields[k] += 1

    return pct, product_fields, analysis_fields


def safety_stats(con_prod):
    """Estadisticas de overallSafetyScore y otros campos numericos."""
    scores = []
    pregnancy_safe = Counter()
    skin_types     = Counter()
    efficacy_keys  = Counter()

    for r in con_prod:
        details  = (r.get("data") or {}).get("details") or {}
        analysis = details.get("analysis") or {}
        if not isinstance(analysis, dict):
            continue

        sc = analysis.get("overallSafetyScore")
        if isinstance(sc, (int, float)):
            scores.append(sc)

        ps = analysis.get("pregnancySafe")
        if ps is not None:
            pregnancy_safe[str(ps)] += 1

        compat = analysis.get("skinTypeCompatibility", {})
        if isinstance(compat, dict):
            for sk, val in compat.items():
                if val:
                    skin_types[sk] += 1

        efficacy = analysis.get("efficacySummary", {})
        if isinstance(efficacy, dict):
            for ek in efficacy:
                efficacy_keys[ek] += 1

    result = {"pregnancy_safe": pregnancy_safe,
              "skin_types": skin_types,
              "efficacy_keys": efficacy_keys}

    if scores:
        result["score_min"]  = round(min(scores), 2)
        result["score_max"]  = round(max(scores), 2)
        result["score_avg"]  = round(sum(scores) / len(scores), 2)
        result["score_count"]= len(scores)
        # distribucion por rango
        dist = Counter()
        for s in scores:
            bucket = f"{int(s)}-{int(s)+1}"
            dist[bucket] += 1
        result["score_dist"] = dict(sorted(dist.items()))
    else:
        result["score_count"] = 0

    return result


# ---------------------------------------------------------------------------
# Generacion de reporte
# ---------------------------------------------------------------------------

def build_report(label, path, c, pct, prod_fields, an_fields, saf):
    lines = []
    total = c["total"]

    lines.append(f"# Análisis: {label}")
    lines.append(f"\n**Archivo:** `{path}`\n")

    # --- Resumen general ---
    lines.append("## Resumen general\n")
    lines.append(f"| Métrica | Valor |")
    lines.append(f"|---|---|")
    lines.append(f"| Total registros | {total:,} |")
    lines.append(f"| Barcodes únicos | {len(c['barcodes']):,} |")
    lines.append(f"| Duplicados | {c['duplicates']:,} |")
    lines.append(f"| **Con producto (éxito)** | **{safe_pct(len(c['con_prod']), total)}** |")
    lines.append(f"| No encontrado (404) | {safe_pct(len(c['not_found']), total)} |")
    lines.append(f"| Errores de scraper | {safe_pct(len(c['errors']), total)} |")
    lines.append(f"| Otros | {safe_pct(len(c['otros']), total)} |")

    # --- Endpoints ---
    if c["endpoints"]:
        lines.append("\n## Endpoints detectados\n")
        lines.append("| Endpoint | Requests |")
        lines.append("|---|---|")
        for ep, cnt in c["endpoints"].most_common():
            lines.append(f"| `{ep}/{{barcode}}` | {cnt:,} |")

    # --- Errores ---
    if c["error_types"]:
        lines.append("\n## Tipos de error\n")
        lines.append("| Error | Cantidad |")
        lines.append("|---|---|")
        for err, cnt in c["error_types"].most_common():
            lines.append(f"| `{err}` | {cnt:,} |")

    # --- Estructura ---
    if pct:
        lines.append("\n## Estructura de respuestas exitosas\n")
        lines.append(f"*(Muestra: {min(len(c['con_prod']), 500):,} registros)*\n")

        lines.append("### Campos `product`\n")
        lines.append("| Campo | Presencia |")
        lines.append("|---|---|")
        for f, cnt in prod_fields.most_common():
            lines.append(f"| `product.{f}` | {safe_pct(cnt, min(len(c['con_prod']), 500))} |")

        lines.append("\n### Campos `details.analysis`\n")
        lines.append("| Campo | Presencia |")
        lines.append("|---|---|")
        for f, cnt in an_fields.most_common():
            lines.append(f"| `analysis.{f}` | {safe_pct(cnt, min(len(c['con_prod']), 500))} |")

    # --- Safety stats ---
    if saf.get("score_count", 0) > 0:
        lines.append("\n## Estadísticas de seguridad\n")
        lines.append("### overallSafetyScore\n")
        lines.append("| Métrica | Valor |")
        lines.append("|---|---|")
        lines.append(f"| Registros con score | {saf['score_count']:,} |")
        lines.append(f"| Mínimo | {saf['score_min']} |")
        lines.append(f"| Máximo | {saf['score_max']} |")
        lines.append(f"| Promedio | {saf['score_avg']} |")

        if saf.get("score_dist"):
            lines.append("\n**Distribución por rango:**\n")
            lines.append("| Rango | Productos |")
            lines.append("|---|---|")
            for bucket, cnt in saf["score_dist"].items():
                lines.append(f"| {bucket} | {cnt:,} |")

        if saf["pregnancy_safe"]:
            lines.append("\n### pregnancySafe\n")
            lines.append("| Valor | Cantidad |")
            lines.append("|---|---|")
            for k, v in saf["pregnancy_safe"].most_common():
                lines.append(f"| {k} | {safe_pct(v, saf['score_count'])} |")

        if saf["skin_types"]:
            lines.append("\n### Compatibilidad por tipo de piel\n")
            lines.append("| Tipo de piel | Productos compatibles |")
            lines.append("|---|---|")
            for sk, cnt in saf["skin_types"].most_common():
                lines.append(f"| {sk} | {cnt:,} |")

        if saf["efficacy_keys"]:
            lines.append("\n### Efectos de eficacia detectados\n")
            lines.append("| Efecto | Productos |")
            lines.append("|---|---|")
            for ek, cnt in saf["efficacy_keys"].most_common():
                lines.append(f"| {ek} | {cnt:,} |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Reporte de comparacion
# ---------------------------------------------------------------------------

def build_comparison(ca, cb, saf_a, saf_b):
    lines = []
    lines.append("# Comparación: pantalla inicio vs entorno de prueba\n")

    lines.append("## Volumen y cobertura\n")
    lines.append(f"| Métrica | pantalla inicio | entorno de prueba |")
    lines.append(f"|---|---|---|")

    def row(label, va, vb):
        lines.append(f"| {label} | {va} | {vb} |")

    row("Total registros",    f"{ca['total']:,}",             f"{cb['total']:,}")
    row("Barcodes únicos",    f"{len(ca['barcodes']):,}",     f"{len(cb['barcodes']):,}")
    row("Con producto",       safe_pct(len(ca['con_prod']),  ca['total']),
                              safe_pct(len(cb['con_prod']),  cb['total']))
    row("No encontrado (404)",safe_pct(len(ca['not_found']), ca['total']),
                              safe_pct(len(cb['not_found']), cb['total']))
    row("Errores",            safe_pct(len(ca['errors']),    ca['total']),
                              safe_pct(len(cb['errors']),    cb['total']))

    # Overlap de barcodes
    bc_a    = ca["barcodes"]
    bc_b    = cb["barcodes"]
    comunes = bc_a & bc_b
    solo_a  = bc_a - bc_b
    solo_b  = bc_b - bc_a

    lines.append("\n## Overlap de barcodes\n")
    lines.append("| | Cantidad |")
    lines.append("|---|---|")
    lines.append(f"| En ambos archivos | {len(comunes):,} |")
    lines.append(f"| Solo en pantalla inicio | {len(solo_a):,} |")
    lines.append(f"| Solo en entorno de prueba | {len(solo_b):,} |")

    # Barcodes con producto en ambos
    bc_prod_a = {r["barcode"] for r in ca["con_prod"]}
    bc_prod_b = {r["barcode"] for r in cb["con_prod"]}
    prod_comun = bc_prod_a & bc_prod_b
    lines.append(f"| Con producto en **ambos** | {len(prod_comun):,} |")
    lines.append(f"| Con producto solo en pantalla inicio | {len(bc_prod_a - bc_prod_b):,} |")
    lines.append(f"| Con producto solo en entorno de prueba | {len(bc_prod_b - bc_prod_a):,} |")

    # Comparacion de safety scores
    lines.append("\n## Comparación de datos de seguridad\n")
    lines.append("| Métrica | pantalla inicio | entorno de prueba |")
    lines.append("|---|---|---|")

    def score_val(saf, key):
        return str(saf.get(key, "N/A")) if saf.get("score_count", 0) > 0 else "N/A"

    row("Registros con score",
        f"{saf_a.get('score_count', 0):,}", f"{saf_b.get('score_count', 0):,}")
    row("Score promedio",  score_val(saf_a, "score_avg"),  score_val(saf_b, "score_avg"))
    row("Score mínimo",    score_val(saf_a, "score_min"),  score_val(saf_b, "score_min"))
    row("Score máximo",    score_val(saf_a, "score_max"),  score_val(saf_b, "score_max"))

    # Diferencia en endpoints
    lines.append("\n## Endpoints\n")
    lines.append("| Script | Endpoint base |")
    lines.append("|---|---|")
    for ep in ca["endpoints"]:
        lines.append(f"| pantalla inicio | `{ep}/{{barcode}}` |")
    for ep in cb["endpoints"]:
        lines.append(f"| entorno de prueba | `{ep}/{{barcode}}` |")

    # Conclusion
    lines.append("\n## Observaciones\n")

    total_con_prod = len(bc_prod_a | bc_prod_b)
    lines.append(f"- **Cobertura combinada**: {total_con_prod:,} barcodes únicos con datos de producto "
                 f"entre ambas fuentes.")

    if len(prod_comun) > 0:
        lines.append(f"- **{len(prod_comun):,} barcodes** tienen respuesta en ambos endpoints — "
                     f"útil para comparar si la data del endpoint autenticado es más rica.")

    if saf_a.get("score_count", 0) > 0 and saf_b.get("score_count", 0) > 0:
        diff = abs(saf_a["score_avg"] - saf_b["score_avg"])
        lines.append(f"- Diferencia en score promedio entre endpoints: **{diff:.2f} puntos**.")

    lines.append(f"- Endpoint `/demo/` es público (sin login) → apto para scraping masivo.")
    lines.append(f"- Endpoint autenticado devuelve datos con mayor nivel de detalle "
                 f"(requiere sesión activa en browser).")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  ANALISIS DE DATOS INCIAPI")
    print("=" * 60)

    print(f"\n[->] Cargando {FILE_A.name} desde pantalla inicio...")
    recs_a = load_jsonl(FILE_A)
    print(f"     {len(recs_a):,} registros cargados.")

    print(f"[->] Cargando {FILE_B.name} desde entorno de prueba...")
    recs_b = load_jsonl(FILE_B)
    print(f"     {len(recs_b):,} registros cargados.")

    print("\n[->] Clasificando...")
    ca = classify(recs_a)
    cb = classify(recs_b)

    print(f"     pantalla inicio  : {len(ca['con_prod']):,} con producto | "
          f"{len(ca['not_found']):,} 404 | {len(ca['errors']):,} errores")
    print(f"     entorno de prueba: {len(cb['con_prod']):,} con producto | "
          f"{len(cb['not_found']):,} 404 | {len(cb['errors']):,} errores")

    print("\n[->] Analizando estructura...")
    pct_a, pf_a, af_a = analyze_structure(ca["con_prod"])
    pct_b, pf_b, af_b = analyze_structure(cb["con_prod"])

    print("[->] Calculando estadisticas de seguridad...")
    saf_a = safety_stats(ca["con_prod"])
    saf_b = safety_stats(cb["con_prod"])

    print("\n[->] Generando reportes...\n")

    # Reporte A
    out_a = BASE_DIR / "analisis_pantalla_inicio.md"
    report_a = build_report(LABEL_A, FILE_A, ca, pct_a, pf_a, af_a, saf_a)
    out_a.write_text(report_a, encoding="utf-8")
    print(f"  [OK] {out_a.name}")

    # Reporte B
    out_b = BASE_DIR / "analisis_entorno_prueba.md"
    report_b = build_report(LABEL_B, FILE_B, cb, pct_b, pf_b, af_b, saf_b)
    out_b.write_text(report_b, encoding="utf-8")
    print(f"  [OK] {out_b.name}")

    # Comparacion
    out_c = BASE_DIR / "analisis_comparacion.md"
    report_c = build_comparison(ca, cb, saf_a, saf_b)
    out_c.write_text(report_c, encoding="utf-8")
    print(f"  [OK] {out_c.name}")

    print("\n" + "=" * 60)
    print("  LISTO — 3 archivos .md generados en scripts/scraping/")
    print("=" * 60)


if __name__ == "__main__":
    main()
