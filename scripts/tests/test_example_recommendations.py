"""
test_example_recommendations.py
=================================
Para cada usuario de ejemplo (3 usuarios con análisis de distintas
condiciones), llama a GET /products/recommendations/{id} y guarda los
resultados en:

  scripts/tests/resultados_recomendaciones_ejemplo.md

Usuarios creados por seed_startup.py:
  ejemplo1@example.com / EjemploPass1!  — acne-excoriated
  ejemplo3@example.com / EjemploPass3!  — rosacea-etr
  ejemplo7@example.com / EjemploPass7!  — rosacea-inflammatory + healthy-skin

Requiere: backend corriendo en localhost:8000
"""

import os
import requests
from datetime import datetime

API_URL  = "http://localhost:8000/api"
CATS     = ["cleanser", "moisturizer", "spf", "serum"]
TOP_N    = 5
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "resultados_recomendaciones_ejemplo.md")

EXAMPLE_USERS = [
    {"email": "ejemplo1@example.com", "password": "EjemploPass1!", "label": "Acné Excoriado"},
    {"email": "ejemplo3@example.com", "password": "EjemploPass3!", "label": "Rosácea ETR"},
    {"email": "ejemplo7@example.com", "password": "EjemploPass7!", "label": "Multi-condición"},
]


# ── helpers ────────────────────────────────────────────────────────────────────

def _login(email, password):
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    return r.json().get("access_token") if r.status_code == 200 else None


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _get_history(token):
    r = requests.get(f"{API_URL}/analysis/history?limit=50", headers=_auth(token))
    return r.json() if r.status_code == 200 else []


def _get_reco(analysis_id, token):
    params = [("categories", c) for c in CATS] + [("top_n", TOP_N)]
    r = requests.get(
        f"{API_URL}/products/recommendations/{analysis_id}",
        headers=_auth(token),
        params=params,
    )
    return r.json() if r.status_code == 200 else None


# ── markdown ───────────────────────────────────────────────────────────────────

def _fmt_analysis(analysis, reco):
    aid      = analysis["id"]
    top1     = analysis.get("top1_label", "?")
    conf     = float(analysis.get("top1_confidence") or 0)
    model    = analysis.get("model_version", "?")
    severity = float(reco.get("severity_score") or 0)
    conds    = reco.get("conditions", [])

    lines = [
        f"### Análisis #{aid} — `{top1}` ({conf:.1%})",
        f"",
        f"> Modelo: `{model}` | Severidad: `{severity:.3f}` | Condiciones activas: **{len(conds)}**",
        "",
    ]

    if len(conds) > 1:
        cond_list = "  ".join(
            f"`{c['condition']}` ({float(c['confidence']):.1%})" for c in conds
        )
        lines += [f"Condiciones detectadas: {cond_list}", ""]

    for cond_data in conds:
        cname      = cond_data["condition"]
        cconf      = float(cond_data.get("confidence") or 0)
        reco_cats  = cond_data.get("recommendations", {})

        if len(conds) > 1:
            lines += [f"#### ↳ `{cname}` ({cconf:.1%})", ""]

        for cat, products in reco_cats.items():
            lines.append(f"**{cat.upper()}**")
            if not products:
                lines.append("_sin productos elegibles en catálogo_")
                lines.append("")
                continue
            for i, p in enumerate(products, 1):
                matched = ", ".join(p.get("matched_ingredients") or []) or "—"
                lines.append(
                    f"{i}. **{p['name']}** — _{p.get('brand') or '?'}_  "
                    f"`score {p['score']}`  matched: {matched}"
                )
            lines.append("")

    return "\n".join(lines)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    sections = [
        "# Recomendaciones — Análisis de Ejemplo",
        "",
        f"> Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}  "
        f"|  Motor: scoring de ingredientes (Opción C)  |  top_n={TOP_N}",
        "",
        "Resultados del endpoint `GET /products/recommendations/{{id}}` para 4 análisis",
        "reales insertados como datos de ejemplo (3 usuarios, distintas condiciones).",
        "",
        "---",
        "",
    ]

    all_ok = True

    for user in EXAMPLE_USERS:
        email = user["email"]
        label = user["label"]
        print(f"\n[→] {email}")
        sections += [f"## {label}", f"`{email}`", ""]

        token = _login(email, user["password"])
        if not token:
            sections += [
                "_⚠️  No se pudo autenticar._",
                "_¿El contenedor corrió seed_startup.py con la nueva función?_",
                "",
            ]
            print("    [ERROR] login falló")
            all_ok = False
            continue

        history   = _get_history(token)
        completed = [a for a in history if a.get("status") == "completed"]

        if not completed:
            sections += ["_Sin análisis completados._", ""]
            print("    [WARN] sin análisis completados")
            continue

        for analysis in completed:
            aid  = analysis["id"]
            top1 = analysis.get("top1_label", "?")
            print(f"    [·] análisis #{aid} ({top1})...", end=" ", flush=True)

            reco = _get_reco(aid, token)
            if not reco:
                sections += [
                    f"_⚠️  Error al obtener recomendaciones para análisis #{aid}_",
                    "",
                ]
                print("ERROR")
                all_ok = False
                continue

            sections.append(_fmt_analysis(analysis, reco))
            sections += ["", "---", ""]

            n_conds = len(reco.get("conditions", []))
            print(f"OK  ({n_conds} condición/es)")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))

    status = "✅ Completado" if all_ok else "⚠️  Completado con errores"
    print(f"\n{status}")
    print(f"MD guardado en: {OUT_PATH}")


if __name__ == "__main__":
    main()
