"""
sitemap_parser.py
Descarga todos los sub-sitemaps de productos de INCIDecoder
y retorna la lista completa de URLs.
"""

import httpx
from lxml import etree

BASE = "https://incidecoder.com"
NS   = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def _get_with_retry(url: str, timeout: int = 60, retries: int = 3) -> httpx.Response:
    """GET con reintentos ante timeout."""
    for attempt in range(1, retries + 1):
        try:
            return httpx.get(url, headers=HEADERS, timeout=timeout)
        except httpx.TimeoutException:
            print(f"   ⚠  Timeout (intento {attempt}/{retries}): {url}")
            if attempt == retries:
                raise
    raise RuntimeError("No debería llegar aquí")


def get_all_product_urls() -> list[str]:
    """
    Lee sitemap-index.xml y descarga cada sub-sitemap de productos.
    Retorna lista de URLs únicas.
    """
    print("↓ Descargando sitemap índice...")
    r = _get_with_retry(f"{BASE}/sitemap-index.xml")
    root = etree.fromstring(r.content)

    all_urls: list[str] = []

    sitemap_locs = root.findall("sm:sitemap/sm:loc", NS)
    product_sitemaps = [s.text for s in sitemap_locs if "sitemap-products" in s.text]

    print(f"   → {len(product_sitemaps)} sub-sitemaps de productos encontrados")

    for i, sitemap_url in enumerate(product_sitemaps):
        print(f"   [{i+1}/{len(product_sitemaps)}] {sitemap_url}")
        try:
            r2 = _get_with_retry(sitemap_url)
            sub = etree.fromstring(r2.content)
            urls = [u.text for u in sub.findall("sm:url/sm:loc", NS)]
            all_urls.extend(urls)
        except Exception as e:
            print(f"   ✗ Error en {sitemap_url}: {e}")

    print(f"\n✓ Total: {len(all_urls)} productos en el sitemap")
    return all_urls


def get_ingredient_urls() -> list[str]:
    """
    Lee los sub-sitemaps de ingredientes.
    """
    print("↓ Descargando sitemap de ingredientes...")
    r = _get_with_retry(f"{BASE}/sitemap-index.xml")
    root = etree.fromstring(r.content)

    all_urls: list[str] = []
    sitemap_locs = root.findall("sm:sitemap/sm:loc", NS)
    ingredient_sitemaps = [s.text for s in sitemap_locs if "sitemap-ingredients" in s.text]

    for sitemap_url in ingredient_sitemaps:
        r2 = _get_with_retry(sitemap_url)
        sub = etree.fromstring(r2.content)
        urls = [u.text for u in sub.findall("sm:url/sm:loc", NS)]
        all_urls.extend(urls)

    print(f"✓ Total: {len(all_urls)} ingredientes en el sitemap")
    return all_urls
