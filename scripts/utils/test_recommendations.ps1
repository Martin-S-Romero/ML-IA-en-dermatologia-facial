# test_recommendations.ps1
# Prueba el motor de recomendaciones con el dataset completo post-batch.
# Testa dos condiciones: rosacea-etr (clinicamente exigente) y acne-comedonal.

$script = @'
import sys
sys.path.insert(0, "/app")
from app.core.database import SessionLocal
from app.core.recommendation_engine import get_recommendations

def print_result(result):
    if result is None:
        print("RESULT IS NONE - analysis no encontrado o user mismatch")
        return
    print(f"Condicion: {result['condition']}  |  Severity: {result['severity_score']}")
    for cat, prods in result["recommendations"].items():
        print(f"\n  === {cat.upper()} ({len(prods)} productos) ===")
        for p in prods:
            score     = p.get("score", 0)
            brand     = p.get("brand", "?")
            name      = p.get("name", "?")
            matched   = p.get("matched_ingredients", [])
            highlights = p.get("highlights") or []
            print(f"    [{score:.1f}] {brand} - {name}")
            if matched:
                print(f"           match: {matched}")
            if highlights:
                print(f"           highlights: {highlights}")

db = SessionLocal()
try:
    # --- Test 1: analysis_id=38 (rosacea-etr, user_id=3) ---
    print("=" * 60)
    print("TEST 1: rosacea-etr (analysis_id=38, user_id=3)")
    print("=" * 60)
    r1 = get_recommendations(db=db, analysis_id=38, user_id=3,
                             categories=["cleanser", "moisturizer", "spf", "serum"], top_n=5)
    print_result(r1)

    # --- Test 2: buscar un analysis con acne ---
    from sqlalchemy import text
    acne_row = db.execute(text(
        "SELECT id, user_id, top1_label FROM analyses WHERE top1_label LIKE '%acne%' LIMIT 1"
    )).fetchone()

    if acne_row:
        print("\n" + "=" * 60)
        print(f"TEST 2: {acne_row[2]} (analysis_id={acne_row[0]}, user_id={acne_row[1]})")
        print("=" * 60)
        r2 = get_recommendations(db=db, analysis_id=acne_row[0], user_id=acne_row[1],
                                 categories=["cleanser", "moisturizer", "spf", "serum"], top_n=5)
        print_result(r2)
    else:
        print("\n[!] No se encontro ningun analisis con condicion acne en BD.")

    # --- Stats de scores ---
    print("\n" + "=" * 60)
    print("STATS: distribucion de scores (rosacea-etr cleanser)")
    print("=" * 60)
    if r1:
        cl = r1["recommendations"].get("cleanser", [])
        scores = [p["score"] for p in cl]
        if scores:
            print(f"  Min: {min(scores):.1f}  Max: {max(scores):.1f}  "
                  f"Rango: {max(scores)-min(scores):.1f}  N: {len(scores)}")

finally:
    db.close()
'@

$script | docker exec -i tesis20-backend-1 python3 -
