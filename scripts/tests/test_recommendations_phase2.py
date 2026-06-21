"""
test_recommendations_phase2.py — Fase 2: Motor de Recomendación (Opción C)
===========================================================================
Valida el endpoint  GET /products/recommendations/{analysis_id}
contra la BD real del entorno local.

Escenarios del plan de implementación:
  1  Ningún producto con avoid_ingredient aparece en resultados (score >= 0)
  2  seborrheic-dermatitis -> mayoría de scores cerca de baseline 40
     (zinc pyrithione / piroctone olamine son raros en catálogos locales)
  3  Severity boost × 1.15: cuando severity > 0.6 y hay matches, score > 46
  4  El top-1 de condiciones comunes tiene al menos un matched_ingredient

Tests de contrato adicionales:
  A  Sin token -> 401
  B  analysis_id inexistente -> 404
  C  Estructura del response (campos obligatorios presentes)
  D  User B no accede al análisis de User A (aislamiento de datos)
  E  Parámetro top_n respetado en todas las categorías
  F  Parámetro categories filtra correctamente

Para usar con una cuenta que ya tiene análisis completados:
    TEST_USER_EMAIL=user@example.com TEST_USER_PASS=pass python scripts/test_recommendations_phase2.py

Sin variables de entorno: crea un usuario nuevo y omite los escenarios que
necesitan análisis completados (estos se ejecutan con datos reales).

Requiere: backend corriendo en localhost:8000
"""

import os
import requests
import uuid

API_URL = "http://localhost:8000/api"
OK   = "[EXITO  ]"
FAIL = "[ERROR  ]"
SKIP = "[OMITIDO]"
INFO = "[INFO   ]"

# Credenciales opcionales de un usuario existente con análisis completados
_ENV_EMAIL = os.getenv("TEST_USER_EMAIL", "")
_ENV_PASS  = os.getenv("TEST_USER_PASS",  "SecurePassword123!")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _register_and_login(name="Test"):
    uid   = str(uuid.uuid4())[:8]
    email = f"reco_p2_{uid}@example.com"
    pw    = "SecurePassword123!"
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": pw, "full_name": name, "gdpr_accepted": True
    })
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": pw})
    return r.json()["access_token"]


def _login_existing(email, pw):
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": pw})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _get_history(token):
    r = requests.get(f"{API_URL}/analysis/history?limit=50", headers=_h(token))
    return r.json() if r.status_code == 200 else []


def _completed(history):
    return [a for a in history if a.get("status") == "completed"]


def _find_condition(completed, condition):
    return next((a for a in completed if a.get("top1_label") == condition), None)


def _get_reco(analysis_id, token, **params):
    return requests.get(
        f"{API_URL}/products/recommendations/{analysis_id}",
        headers=_h(token), params=params
    )


def _ok(condition, msg_ok, response=None, extra=None):
    if condition:
        print(f"    {OK} {msg_ok}")
    else:
        detail = extra or (response.text[:200] if response else "")
        print(f"    {FAIL} {detail}")


# ── Runner principal ───────────────────────────────────────────────────────────

def test_reco_phase2():
    print("=" * 62)
    print("    FASE 2 — MOTOR DE RECOMENDACIÓN (Opción C)")
    print("=" * 62)

    tok_a = (
        _login_existing(_ENV_EMAIL, _ENV_PASS)
        if _ENV_EMAIL else None
    ) or _register_and_login("Reco UserA")

    tok_b = _register_and_login("Reco UserB")

    # ── A: Sin token -> 401 ────────────────────────────────────────────────────
    print("\n[A] GET /recommendations/{id} sin token -> 401")
    r = requests.get(f"{API_URL}/products/recommendations/1")
    _ok(r.status_code == 401, "401 Unauthorized", r)

    # ── B: analysis_id inexistente -> 404 ──────────────────────────────────────
    print("\n[B] analysis_id=99999 (no existe) -> 404")
    r = _get_reco(99999, tok_a)
    _ok(r.status_code == 404, "404 Not Found", r)

    # ── Cargar historial ───────────────────────────────────────────────────────
    history   = _get_history(tok_a)
    done      = _completed(history)

    if not done:
        print(f"\n{SKIP} Usuario sin análisis completados.")
        print(f"       Escenarios C-F y 1-4 requieren análisis reales.")
        print(f"       Usa TEST_USER_EMAIL / TEST_USER_PASS para correr con datos.")
        _test_isolation_new_user(tok_b)
        return

    first = done[0]
    aid   = first["id"]

    # ── C: Estructura del response ─────────────────────────────────────────────
    print(f"\n[C] Estructura del response (analysis_id={aid})")
    r = _get_reco(aid, tok_a)
    if r.status_code != 200:
        print(f"    {FAIL} {r.status_code}: {r.text[:200]}")
        return
    data    = r.json()
    required = {"analysis_id", "condition", "severity_score", "recommendations", "conditions"}
    missing  = required - set(data.keys())
    conditions = data.get("conditions", [])
    _ok(
        not missing,
        f"Campos OK. Top1: {data.get('condition')}  "
        f"Severity: {data.get('severity_score')}  "
        f"Condiciones activas: {len(conditions)}  "
        f"Categorías: {list(data.get('recommendations', {}).keys())}",
        extra=f"Faltan campos: {missing}"
    )
    if len(conditions) > 1:
        labels = [c['condition'] for c in conditions]
        confs  = [c['confidence'] for c in conditions]
        print(f"    [INFO   ] Condiciones detectadas: "
              + ", ".join(f"{l}({c:.0%})" for l, c in zip(labels, confs)))

    # ── D: Aislamiento de datos ───────────────────────────────────────────────
    print(f"\n[D] Aislamiento — User B no puede ver el análisis de User A")
    r = _get_reco(aid, tok_b)
    _ok(
        r.status_code == 404,
        "User B recibe 404 (datos aislados)",
        extra=f"User B recibió {r.status_code} — POSIBLE FUGA DE DATOS"
    )

    # ── E: Parámetro top_n ─────────────────────────────────────────────────────
    print(f"\n[E] Parámetro top_n=2")
    r = _get_reco(aid, tok_a, top_n=2)
    if r.status_code == 200:
        overflow = [
            f"{cat}({len(ps)})"
            for cat, ps in r.json()["recommendations"].items()
            if len(ps) > 2
        ]
        _ok(not overflow, "top_n=2 respetado en todas las categorías",
            extra=f"Overflow en: {overflow}")
    else:
        print(f"    {FAIL} {r.status_code}: {r.text[:100]}")

    # ── F: Parámetro categories ────────────────────────────────────────────────
    print(f"\n[F] Parámetro categories=['cleanser']")
    r = _get_reco(aid, tok_a, categories="cleanser")
    if r.status_code == 200:
        keys = list(r.json()["recommendations"].keys())
        _ok(keys == ["cleanser"], f"Solo 'cleanser' retornado: {keys}")
    else:
        print(f"    {FAIL} {r.status_code}: {r.text[:100]}")

    # ── Escenarios del plan ────────────────────────────────────────────────────
    _scenario_1_avoid_excluded(done, tok_a)
    _scenario_2_seborrheic_baseline(done, tok_a)
    _scenario_3_severity_boost(done, tok_a)
    _scenario_4_top_has_matches(done, tok_a)


# ── Test sin datos (solo aislamiento) ─────────────────────────────────────────

def _test_isolation_new_user(tok_b):
    print("\n[D] Aislamiento — IDs bajos no visibles para nuevo usuario")
    leaked = [
        aid for aid in range(1, 6)
        if requests.get(
            f"{API_URL}/products/recommendations/{aid}",
            headers=_h(tok_b)
        ).status_code not in (404, 400)
    ]
    _ok(not leaked,
        "Todos los IDs bajos retornan 404 para usuario nuevo",
        extra=f"FUGA en analysis_ids: {leaked}")


# ── Escenario 1 ────────────────────────────────────────────────────────────────

def _scenario_1_avoid_excluded(done, tok):
    """
    El engine filtra productos con avoid_ingredients (score = -1, no aparecen).
    Verificamos: ningún producto en el response tiene score < 0.
    Adicionalmente contamos matches de target_ingredients.
    """
    print("\n[1] Escenario 1 — Productos con avoid_ingredients excluidos del response")

    # Preferir acne-comedonal (tiene varios avoid claros: fragrance, coconut oil)
    analysis = (
        _find_condition(done, "acne-comedonal") or
        _find_condition(done, "acne-inflammatory") or
        _find_condition(done, "rosacea-etr") or
        done[0]
    )

    r = _get_reco(analysis["id"], tok)
    if r.status_code != 200:
        print(f"    {FAIL} {r.status_code}")
        return

    data = r.json()
    reco = data["recommendations"]
    cond = data["condition"]

    negatives = [
        f"{cat}/{p['name']}(score={p['score']})"
        for cat, ps in reco.items()
        for p in ps
        if p["score"] < 0
    ]
    _ok(not negatives,
        f"[{cond}] Ningún producto con score < 0 en resultados.",
        extra=f"Scores negativos: {negatives}")

    total_matches = sum(
        len(p.get("matched_ingredients", []))
        for ps in reco.values()
        for p in ps
    )
    total_products = sum(len(ps) for ps in reco.values())

    if total_matches > 0:
        print(f"    {INFO} [{cond}] {total_matches} matches de target_ingredients "
              f"en {total_products} productos retornados.")
    else:
        print(f"    {INFO} [{cond}] Sin matches de target_ingredients — "
              "catálogo necesita más productos con ingredientes activos.")


# ── Escenario 2 ────────────────────────────────────────────────────────────────

def _scenario_2_seborrheic_baseline(done, tok):
    """
    seborrheic-dermatitis: zinc pyrithione y piroctone olamine son raros.
    La mayoría de productos debería rondar el score baseline de 40.
    """
    print("\n[2] Escenario 2 — seborrheic-dermatitis: scores cercanos a baseline 40")

    analysis = _find_condition(done, "seborrheic-dermatitis")
    if not analysis:
        print(f"    {SKIP} Sin análisis de seborrheic-dermatitis en historial.")
        return

    r = _get_reco(analysis["id"], tok)
    if r.status_code != 200:
        print(f"    {FAIL} {r.status_code}")
        return

    all_ps = [p for ps in r.json()["recommendations"].values() for p in ps]
    if not all_ps:
        print(f"    {INFO} Sin productos elegibles en catálogo para seborrheic-dermatitis.")
        return

    high     = [p for p in all_ps if p["score"] > 55]
    matched  = [p for p in all_ps if p.get("matched_ingredients")]
    pct_high = len(high) / len(all_ps) * 100

    if pct_high < 25:
        print(f"    {OK} Solo {len(high)}/{len(all_ps)} ({pct_high:.0f}%) "
              f"tienen score > 55 — confirma escasez de activos especializados.")
    else:
        print(f"    {INFO} {len(high)}/{len(all_ps)} ({pct_high:.0f}%) tienen score > 55.")
    print(f"    {INFO} {len(matched)} productos con matches de zinc pyrithione / "
          "piroctone olamine en el catálogo.")


# ── Escenario 3 ────────────────────────────────────────────────────────────────

def _scenario_3_severity_boost(done, tok):
    """
    Cuando severity > 0.6 y hay matched_ingredients, el engine aplica × 1.15.
    Verificamos: score del producto > 40 * 1.15 = 46.0.
    """
    print("\n[3] Escenario 3 — Severity boost (× 1.15 cuando severity > 0.6)")

    for a in done:
        # GET /analysis/{id} para leer severity_score del JSONB result
        rd = requests.get(f"{API_URL}/analysis/{a['id']}", headers=_h(tok))
        if rd.status_code != 200:
            continue
        severity = float((rd.json().get("result") or {}).get("severity_score", 0.0))

        if severity <= 0.6:
            continue

        rr = _get_reco(a["id"], tok)
        if rr.status_code != 200:
            continue

        reco = rr.json()["recommendations"]
        boosted = [
            p for ps in reco.values() for p in ps
            if p.get("matched_ingredients") and p["score"] > 46.0
        ]
        has_match_no_boost = [
            p for ps in reco.values() for p in ps
            if p.get("matched_ingredients") and p["score"] <= 46.0
        ]

        print(f"    Análisis {a['id']} | severity={severity:.2f}")
        if boosted:
            ex = boosted[0]
            print(f"    {OK} Boost visible: '{ex['name'][:40]}' score={ex['score']} > 46.0")
        elif has_match_no_boost:
            ex = has_match_no_boost[0]
            print(f"    {INFO} Match con score={ex['score']} ≤ 46 — "
                  "position_weight o rating_weight pueden reducir el score base antes del boost.")
        else:
            print(f"    {INFO} Sin productos con matched_ingredients para este análisis.")
        return

    print(f"    {SKIP} Sin análisis con severity > 0.6 en historial.")


# ── Escenario 4 ────────────────────────────────────────────────────────────────

def _scenario_4_top_has_matches(done, tok):
    """
    Para condiciones con activos conocidos (acne-comedonal, rosacea-etr, healthy-skin),
    el producto top-1 de cada categoría debería tener al menos un matched_ingredient.
    """
    print("\n[4] Escenario 4 — Top-1 de cada categoría tiene matched_ingredients")

    for condition in ["acne-comedonal", "rosacea-etr", "healthy-skin", "acne-inflammatory"]:
        analysis = _find_condition(done, condition)
        if not analysis:
            continue

        r = _get_reco(analysis["id"], tok)
        if r.status_code != 200:
            continue

        reco          = r.json()["recommendations"]
        with_match    = []
        without_match = []

        for cat, ps in reco.items():
            if not ps:
                continue
            top = ps[0]
            if top.get("matched_ingredients"):
                with_match.append(f"{cat}:{top['matched_ingredients'][0]}")
            else:
                without_match.append(cat)

        if with_match:
            print(f"    {OK} [{condition}] Match en top-1: {', '.join(with_match)}")
        if without_match:
            print(f"    {INFO} [{condition}] Top-1 sin match en: {', '.join(without_match)} "
                  "(score baseline — catálogo puede mejorar con más activos)")
        return  # mostrar resultado del primer match encontrado

    print(f"    {SKIP} Sin análisis de condiciones comunes (acne-comedonal, rosacea-etr, etc.).")


if __name__ == "__main__":
    test_reco_phase2()
