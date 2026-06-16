"""
main.py
Orquestador del scraper de INCIDecoder.

Modos de uso (correr desde backend/scraper/):
  python main.py test           → solo 5 productos para verificar que funciona
  python main.py priority       → solo marcas clave (~500-1000 productos, ~1 hora)
  python main.py batch 500      → próximos N productos pendientes (default 500)
  python main.py full           → todo el catálogo (44,000+ productos, ~2 días)
"""

import sys
import time
from sitemap_parser import get_all_product_urls
from product_scraper import scrape_product
from db_writer import save_product, already_scraped

# ── Marcas prioritarias para el modo "priority" ────────────────────────────────
PRIORITY_BRANDS = [
    # ── Dermatología clínica (recomendadas por dermatólogos) ───────────────────
    "cerave",
    "la-roche-posay",
    "cetaphil",
    "eucerin",
    "aveeno",
    "skinceuticals",
    "eltamd",
    "elta-md",
    "isdin",
    "uriage",
    "svr",
    "avene",
    "bioderma",
    "vichy",
    "sesderma",

    # ── Activos / evidencia científica ────────────────────────────────────────
    "the-ordinary",
    "ordinary",
    "paulas-choice",
    "paula-s-choice",
    "differin",
    "inkey",          # The INKEY List

    # ── Masivas / farmacias y supermercados ───────────────────────────────────
    "neutrogena",
    "olay",
    "nivea",
    "garnier",
    "loreal",         # L'Oréal Paris
    "ponds",          # Pond's
    "roc",            # RoC Retinol

    # ── Premium / tiendas departamentales ─────────────────────────────────────
    "clinique",
    "kiehls",         # Kiehl's
    "drunk-elephant",
    "mario-badescu",

    # ── K-beauty (popular en acné y piel sensible) ────────────────────────────
    "cosrx",
    "purito",
    "some-by-mi",
    "skin1004",
    "beauty-of-joseon",
]


def filter_priority(urls: list[str]) -> list[str]:
    return [
        u for u in urls
        if any(brand in u.lower() for brand in PRIORITY_BRANDS)
    ]


def run(mode: str = "priority", batch_size: int = 500):
    print(f"\n◆ INCIDecoder Scraper — modo: {mode}\n{'─'*50}")

    # 1. Obtener todas las URLs del sitemap
    all_urls = get_all_product_urls()

    # 2. Filtrar según el modo
    if mode == "test":
        urls = all_urls[:5]
        print(f"[test] Modo test: {len(urls)} productos")

    elif mode == "priority":
        urls = filter_priority(all_urls)
        print(f"[*]  Modo priority: {len(urls)} productos de marcas clave")

    elif mode == "batch":
        pending = [u for u in all_urls if not already_scraped(u)]
        urls = pending[:batch_size]
        print(f"▶  Modo batch: {len(urls)} productos (de {len(pending)} pendientes)")

    elif mode == "full":
        urls = [u for u in all_urls if not already_scraped(u)]
        print(f"◉  Modo full: {len(urls)} productos pendientes")
        estimated_hours = len(urls) * 4.5 / 3600
        print(f"   Tiempo estimado: {estimated_hours:.1f} horas (delay ~4.5s/req)")

    else:
        print(f"[x] Modo desconocido: {mode}")
        print("   Usa: test | priority | batch [N] | full")
        return

    if not urls:
        print("[ok] No hay productos pendientes.")
        return

    # 3. Scraping
    saved   = 0
    skipped = 0
    errors  = 0
    start   = time.time()

    for i, url in enumerate(urls, 1):
        elapsed = time.time() - start
        eta = (elapsed / i) * (len(urls) - i) if i > 1 else 0
        print(f"\n[{i}/{len(urls)}] ETA: {eta/60:.0f}min | {url}")

        if already_scraped(url):
            print("  → Ya en BD, skip")
            skipped += 1
            continue

        product = scrape_product(url)

        if not product:
            errors += 1
            continue

        ok = save_product(product)

        if ok:
            saved += 1
            print(f"  [ok] {product.brand} - {product.name} | {len(product.ingredients)} ingredientes")
        else:
            skipped += 1

    # 4. Resumen
    total_time = time.time() - start
    print(f"\n{'─'*50}")
    print(f"[ok] Scraping finalizado en {total_time/60:.1f} minutos")
    print(f"   Guardados: {saved}")
    print(f"   Skipped:   {skipped}")
    print(f"   Errores:   {errors}")


if __name__ == "__main__":
    mode       = sys.argv[1] if len(sys.argv) > 1 else "priority"
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    run(mode=mode, batch_size=batch_size)
