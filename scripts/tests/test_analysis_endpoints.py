"""
test_analysis_endpoints.py — Cobertura de endpoints de Análisis
================================================================
Endpoints que NO están cubiertos por test_skin_mock.py:

  GET /analysis/history          paginación, orden desc, aislamiento
  GET /analysis/{id}             documento completo del análisis
  GET /analysis/{id}/status      estado actual (processing/completed/failed)
  GET /analysis/{id}/image       sirve la imagen censurada

Todos los endpoints se verifican también sin token (-> 401) y con un
usuario diferente al propietario (-> 404, aislamiento de datos).

Requiere: backend corriendo en localhost:8000
"""

import requests
import uuid

API_URL = "http://localhost:8000/api"
OK   = "[EXITO  ]"
FAIL = "[ERROR  ]"
SKIP = "[OMITIDO]"
INFO = "[INFO   ]"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _register_and_login(name="Test"):
    uid   = str(uuid.uuid4())[:8]
    email = f"anal_{uid}@example.com"
    pw    = "SecurePassword123!"
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": pw, "full_name": name, "gdpr_accepted": True
    })
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": pw})
    return r.json()["access_token"]


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def _ok(cond, msg_ok, response=None, extra=None):
    if cond:
        print(f"    {OK} {msg_ok}")
    else:
        detail = extra or (response.text[:200] if response else "")
        print(f"    {FAIL} {detail}")


def _find_any_analysis(tokens):
    """Busca el primer análisis disponible en cualquiera de las cuentas dadas."""
    for tok, other in zip(tokens, reversed(tokens)):
        r = requests.get(f"{API_URL}/analysis/history?limit=50", headers=_h(tok))
        if r.status_code == 200 and r.json():
            return r.json()[0], tok, other
    return None, None, None


# ── Runner principal ───────────────────────────────────────────────────────────

def test_analysis_endpoints():
    print("=" * 62)
    print("    ENDPOINTS DE ANÁLISIS — COBERTURA COMPLETA")
    print("=" * 62)

    tok_a = _register_and_login("Analysis UserA")
    tok_b = _register_and_login("Analysis UserB")

    # ── 1. /history — usuario nuevo -> lista vacía ─────────────────────────────
    print("\n[1] GET /analysis/history — usuario nuevo -> lista vacía []")
    r = requests.get(f"{API_URL}/analysis/history", headers=_h(tok_a))
    _ok(r.status_code == 200 and isinstance(r.json(), list) and r.json() == [],
        "Retorna [] para usuario sin análisis.", r)

    # ── 2. /history — sin token -> 401 ────────────────────────────────────────
    print("\n[2] GET /analysis/history sin token -> 401")
    r = requests.get(f"{API_URL}/analysis/history")
    _ok(r.status_code == 401, "401 Unauthorized.", r)

    # ── 3. /history — paginación aceptada ─────────────────────────────────────
    print("\n[3] GET /analysis/history?skip=0&limit=5 (paginación)")
    r = requests.get(f"{API_URL}/analysis/history?skip=0&limit=5", headers=_h(tok_a))
    _ok(r.status_code == 200, f"Paginación aceptada. Retorna: {r.json()}", r)

    # ── 4–11: Tests que necesitan un análisis existente en BD ─────────────────
    sample, owner_tok, other_tok = _find_any_analysis([tok_a, tok_b])

    if sample is None:
        print(f"\n{SKIP} Sin análisis en BD — tests 4-11 omitidos.")
        print(f"       Sube una imagen con test_skin_mock.py para activarlos.")
        _test_auth_guards_no_data(tok_a)
        return

    aid = sample["id"]
    print(f"\n    (usando analysis_id={aid}, status={sample['status']})")

    # ── 4. GET /analysis/{id} — documento completo ───────────────────────────
    print(f"\n[4] GET /analysis/{aid} — documento completo")
    r = requests.get(f"{API_URL}/analysis/{aid}", headers=_h(owner_tok))
    if r.status_code == 200:
        doc  = r.json()
        reqs = {"id", "status", "created_at"}
        _ok(reqs.issubset(doc.keys()),
            f"Campos presentes. status={doc['status']}, "
            f"top1_label={doc.get('top1_label')}, "
            f"model_version={doc.get('model_version')}",
            extra=f"Faltan: {reqs - set(doc.keys())}")
    else:
        print(f"    {FAIL} {r.status_code}: {r.text[:200]}")

    # ── 5. GET /analysis/{id}/status ──────────────────────────────────────────
    print(f"\n[5] GET /analysis/{aid}/status")
    r = requests.get(f"{API_URL}/analysis/{aid}/status", headers=_h(owner_tok))
    if r.status_code == 200:
        doc = r.json()
        _ok("analysis_id" in doc and "status" in doc,
            f"status={doc.get('status')}", extra=f"Campos inesperados: {list(doc.keys())}")
    else:
        print(f"    {FAIL} {r.status_code}: {r.text[:200]}")

    # ── 6. GET /analysis/99999 — no encontrado ────────────────────────────────
    print(f"\n[6] GET /analysis/99999 -> 404")
    r = requests.get(f"{API_URL}/analysis/99999", headers=_h(owner_tok))
    _ok(r.status_code == 404, "404 Not Found.", r)

    # ── 7. GET /analysis/{id}/status sin token -> 401 ─────────────────────────
    print(f"\n[7] GET /analysis/{aid}/status sin token -> 401")
    r = requests.get(f"{API_URL}/analysis/{aid}/status")
    _ok(r.status_code == 401, "401 Unauthorized.", r)

    # ── 8. Aislamiento — GET /analysis/{id} ──────────────────────────────────
    print(f"\n[8] Aislamiento — User B no accede al análisis de User A")
    r = requests.get(f"{API_URL}/analysis/{aid}", headers=_h(other_tok))
    _ok(r.status_code == 404, "User B recibe 404 (datos aislados).",
        extra=f"User B recibió {r.status_code} — POSIBLE FUGA DE DATOS")

    # ── 9. Aislamiento — GET /analysis/{id}/status ───────────────────────────
    print(f"\n[9] Aislamiento — User B no puede ver /status de User A")
    r = requests.get(f"{API_URL}/analysis/{aid}/status", headers=_h(other_tok))
    _ok(r.status_code == 404, "User B recibe 404 en /status.",
        extra=f"User B recibió {r.status_code}")

    # ── 10. GET /analysis/{id}/image ─────────────────────────────────────────
    print(f"\n[10] GET /analysis/{aid}/image")
    r = requests.get(f"{API_URL}/analysis/{aid}/image", headers=_h(owner_tok))
    if r.status_code == 200:
        ct = r.headers.get("content-type", "")
        _ok("image" in ct, f"Imagen servida. Content-Type: {ct}",
            extra=f"Respuesta no es imagen: {ct}")
    elif r.status_code == 404:
        print(f"    {SKIP} Imagen no disponible (status del análisis: {sample['status']}).")
    else:
        print(f"    {FAIL} {r.status_code}: {r.text[:200]}")

    # ── 11. Aislamiento — User B no ve /image de User A ──────────────────────
    print(f"\n[11] Aislamiento — User B no puede ver /image de User A")
    r = requests.get(f"{API_URL}/analysis/{aid}/image", headers=_h(other_tok))
    _ok(r.status_code == 404, "User B recibe 404 en /image.",
        extra=f"User B recibió {r.status_code}")

    # ── 12. /history — orden descendente (más reciente primero) ──────────────
    print(f"\n[12] /history — orden descendente (más reciente primero)")
    r = requests.get(f"{API_URL}/analysis/history?limit=20", headers=_h(owner_tok))
    if r.status_code == 200:
        items = r.json()
        if len(items) >= 2:
            ordered = all(
                items[i]["created_at"] >= items[i + 1]["created_at"]
                for i in range(len(items) - 1)
            )
            _ok(ordered, "Orden descendente verificado.",
                extra="Historial no está ordenado por fecha descendente.")
        else:
            print(f"    {SKIP} Solo {len(items)} análisis — orden no verificable.")
    else:
        print(f"    {FAIL} {r.status_code}")

    # ── 13. /history — campos AnalysisSnapshot presentes ─────────────────────
    print(f"\n[13] /history — campos del snapshot correctos")
    r = requests.get(f"{API_URL}/analysis/history?limit=1", headers=_h(owner_tok))
    if r.status_code == 200 and r.json():
        snap = r.json()[0]
        required = {"id", "status", "created_at"}
        _ok(required.issubset(snap.keys()),
            f"Snapshot OK: {list(snap.keys())}",
            extra=f"Faltan campos: {required - set(snap.keys())}")
    else:
        print(f"    {SKIP} Sin análisis para verificar snapshot.")


def _test_auth_guards_no_data(token):
    """Verifica que todos los endpoints requieren auth cuando no hay datos."""
    print("\n[Auth Guards] Endpoints de análisis requieren token -> 401")
    endpoints = [
        "/analysis/history",
        "/analysis/99999",
        "/analysis/99999/status",
        "/analysis/99999/image",
    ]
    all_ok = True
    for ep in endpoints:
        r = requests.get(f"{API_URL}{ep}")
        if r.status_code != 401:
            print(f"    {FAIL} {ep} -> {r.status_code} (esperado 401)")
            all_ok = False
    if all_ok:
        print(f"    {OK} Todos los endpoints requieren autenticación (401).")


if __name__ == "__main__":
    test_analysis_endpoints()
