import sys, os
sys.path.insert(0, "/app")
from app.core.database import SessionLocal
from app.core.recommendation_engine import get_recommendations

db = SessionLocal()
try:
    result = get_recommendations(db=db, analysis_id=38, user_id=3, categories=["cleanser", "moisturizer", "spf", "serum"], top_n=3)
    if result is None:
        print("RESULT IS NONE - analysis not found or user mismatch")
    else:
        print(f"Condicion: {result['condition']}  |  Severity: {result['severity_score']}")
        for cat, prods in result["recommendations"].items():
            print(f"\n=== {cat.upper()} ({len(prods)} productos) ===")
            for p in prods:
                score = p.get("score", 0)
                brand = p.get("brand", "?")
                name = p.get("name", "?")
                matched = p.get("matched_ingredients", [])
                highlights = p.get("highlights", [])
                print(f"  [{score:.1f}] {brand} - {name}")
                if matched:
                    print(f"         matched: {matched}")
                if highlights:
                    print(f"         highlights: {highlights}")
finally:
    db.close()
