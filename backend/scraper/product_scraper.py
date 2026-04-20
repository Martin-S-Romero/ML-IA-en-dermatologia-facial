"""
product_scraper.py
Extrae nombre, marca, descripción e ingredientes de una página
de producto de INCIDecoder usando los selectores HTML confirmados.
"""

import httpx
import time
import random
from dataclasses import dataclass, field
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class ScrapedIngredient:
    inci_name:  str
    function:   str        # "solvent", "emollient", etc.
    rating:     str        # "Superstar", "Good stuff", "OK", "Caution", ""
    irr_com:    str        # irritancy/comedogenicity: "0, 0" etc.
    position:   int        # orden en la fórmula (1 = primero = mayor concentración)
    detail_url: str = ""   # /ingredients/glycerin


@dataclass
class ScrapedProduct:
    name:        str
    brand:       str
    description: str
    source_url:  str
    highlights:  list[str]               = field(default_factory=list)   # ["#alcohol-free", ...]
    ingredients: list[ScrapedIngredient] = field(default_factory=list)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    return " ".join(text.split()).strip()


def _rate_limit():
    """Pausa aleatoria respetuosa entre requests (3–6 segundos)."""
    time.sleep(random.uniform(3.0, 6.0))


# ── Extractor principal ────────────────────────────────────────────────────────

def scrape_product(url: str) -> ScrapedProduct | None:
    """
    Descarga y parsea una página de producto de INCIDecoder.

    Selectores confirmados con DevTools:
      - Marca:       span#product-brand-title
      - Nombre:      span#product-title
      - Descripción: span#product-details
      - Highlights:  div.paddingb20.hashtags > a  (los #tags)
      - Tabla skim:  table.product-skim > tbody > tr
          · td[0]: a.ingred-detail-link  (nombre INCI + link)
          · td[1]: texto plano           (what-it-does / función)
          · td[2]: texto plano           (irr./com.)
          · td[3]: texto plano           (ID-Rating)
    """
    _rate_limit()

    try:
        r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)

        if r.status_code == 429:
            print(f"  ⚠  Rate limited. Esperando 60s...")
            time.sleep(60)
            r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)

        if r.status_code != 200:
            print(f"  ✗ HTTP {r.status_code} → {url}")
            return None

        soup = BeautifulSoup(r.text, "lxml")

        # ── Datos básicos del producto ──────────────────────────────────────
        brand_el = soup.select_one("span#product-brand-title")
        title_el = soup.select_one("span#product-title")
        desc_el  = soup.select_one("span#product-details")

        brand       = _clean(brand_el.get_text()) if brand_el else ""
        name        = _clean(title_el.get_text()) if title_el else ""
        description = _clean(desc_el.get_text())  if desc_el  else ""

        if not name:
            print(f"  ✗ No se encontró nombre en {url}")
            return None

        # ── Highlights (#tags) ──────────────────────────────────────────────
        highlights: list[str] = []
        hashtag_div = soup.select_one("div.paddingb20.hashtags")
        if hashtag_div:
            highlights = [_clean(a.get_text()) for a in hashtag_div.select("a")]

        # ── Tabla "Skim through" ────────────────────────────────────────────
        ingredients: list[ScrapedIngredient] = []
        table = soup.select_one("table.product-skim")

        if table:
            rows = table.select("tbody tr")
            position = 1

            for row in rows:
                tds = row.find_all("td")
                if len(tds) < 2:
                    continue

                # td[0] → nombre INCI + link
                a_tag = tds[0].find("a", class_="ingred-detail-link")
                if not a_tag:
                    continue

                inci_name  = _clean(a_tag.get_text())
                detail_url = a_tag.get("href", "")

                # td[1] → función (what-it-does)
                function = _clean(tds[1].get_text()) if len(tds) > 1 else ""

                # td[2] → irritancy / comedogenicity
                irr_com  = _clean(tds[2].get_text()) if len(tds) > 2 else ""

                # td[3] → ID-Rating ("Superstar", "Good stuff", "Caution", etc.)
                rating   = _clean(tds[3].get_text()) if len(tds) > 3 else ""

                ingredients.append(ScrapedIngredient(
                    inci_name=inci_name,
                    function=function,
                    rating=rating,
                    irr_com=irr_com,
                    position=position,
                    detail_url=detail_url,
                ))
                position += 1

        return ScrapedProduct(
            name=name,
            brand=brand,
            description=description,
            source_url=url,
            highlights=highlights,
            ingredients=ingredients,
        )

    except httpx.TimeoutException:
        print(f"  ✗ Timeout en {url}")
        return None
    except Exception as e:
        print(f"  ✗ Error inesperado en {url}: {e}")
        return None
