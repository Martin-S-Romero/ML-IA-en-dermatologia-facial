#!/usr/bin/env python3
"""
sniffer.py v3 — estrategia DOM

El playground calcula overallSafetyScore, skinCompatibility, etc. en el cliente
con JavaScript. No hay segundo endpoint de red.

Esta version:
1. Captura la respuesta de red normal (/api/web/products/{barcode})
2. Espera a que el JS renderice el resultado
3. Lee el JSON de la seccion "Respuesta JSON sin procesar" directamente del DOM
4. Guarda AMBAS cosas: el body de red + el JSON renderizado por el cliente

Resultado:
  sniffer_resultado.json  — ambos JSONs para el barcode de prueba
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).parent
LOGIN_URL  = "https://inciapi.com/login"
TARGET_URL = "https://inciapi.com/dashboard/playground"

LOGIN_EMAIL = "sheens0graviti+inciapi@gmail.com"
LOGIN_PASS  = "64544249"

BARCODE     = "7310617311936"
OUTPUT_JSON = BASE_DIR / "sniffer_resultado.json"

# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

async def do_login(page):
    print(f"[->] Login...")
    await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(1.5)

    email_sel = None
    for sel in ['input[type="email"]', 'input[name*="email" i]',
                'input[placeholder*="correo" i]', 'input[type="text"]']:
        try:
            if await page.locator(sel).first.count() > 0:
                email_sel = sel; break
        except Exception:
            continue

    pass_sel = None
    for sel in ['input[type="password"]', 'input[name*="pass" i]',
                'input[placeholder*="contrase" i]']:
        try:
            if await page.locator(sel).first.count() > 0:
                pass_sel = sel; break
        except Exception:
            continue

    if not email_sel or not pass_sel:
        await page.screenshot(path=str(BASE_DIR / "sniffer_login_debug.png"))
        return False

    await page.locator(email_sel).first.fill(LOGIN_EMAIL)
    await asyncio.sleep(0.3)
    await page.locator(pass_sel).first.fill(LOGIN_PASS)
    await asyncio.sleep(0.3)

    submit_sel = None
    for sel in ['button[type="submit"]', 'button:has-text("Iniciar")',
                'button:has-text("Login")', 'button']:
        try:
            if await page.locator(sel).first.count() > 0:
                submit_sel = sel; break
        except Exception:
            continue

    if submit_sel:
        await page.locator(submit_sel).first.click()
    else:
        await page.locator(pass_sel).first.press("Enter")

    try:
        await page.wait_for_url(lambda url: "login" not in url.lower(), timeout=15000)
        print("[OK] Login exitoso.")
        return True
    except PlaywrightTimeout:
        await page.screenshot(path=str(BASE_DIR / "sniffer_login_debug.png"))
        return False


# ---------------------------------------------------------------------------
# Extraer JSON del DOM
# ---------------------------------------------------------------------------

async def extract_dom_json(page):
    """
    Busca el bloque de texto que contiene el JSON renderizado por el playground.
    Intenta varios selectores posibles para la seccion 'Respuesta JSON sin procesar'.
    """
    candidates = [
        # Bloques de codigo / pre con JSON
        'pre',
        'code',
        '[class*="json"]',
        '[class*="response"]',
        '[class*="raw"]',
        '[class*="result"]',
        '[class*="output"]',
        # Texto que contenga overallSafetyScore
        'text="overallSafetyScore"',
    ]

    # Estrategia 1: buscar <pre> o <code> que contenga el JSON
    for sel in ['pre', 'code', '[class*="json"]', '[class*="raw"]',
                '[class*="response"]', '[class*="result"]', '[class*="output"]']:
        try:
            elements = await page.locator(sel).all()
            for el in elements:
                text = (await el.inner_text()).strip()
                if "overallSafetyScore" in text or "skinCompatibility" in text:
                    try:
                        return json.loads(text), sel
                    except Exception:
                        # Puede tener texto extra antes/despues
                        start = text.find("{")
                        end   = text.rfind("}") + 1
                        if start >= 0 and end > start:
                            try:
                                return json.loads(text[start:end]), sel
                            except Exception:
                                pass
        except Exception:
            continue

    # Estrategia 2: buscar en todo el texto de la pagina
    try:
        full_text = await page.evaluate("() => document.body.innerText")
        idx = full_text.find('"overallSafetyScore"')
        if idx >= 0:
            # Retroceder hasta el { que abre el objeto
            start = full_text.rfind("{", 0, idx)
            if start >= 0:
                # Encontrar el } de cierre contando brackets
                depth = 0
                end   = start
                for i, ch in enumerate(full_text[start:], start):
                    if ch == "{": depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                try:
                    return json.loads(full_text[start:end]), "body.innerText"
                except Exception:
                    pass
    except Exception:
        pass

    return None, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    print("=" * 60)
    print(f"  SNIFFER v3 — lectura DOM — barcode: {BARCODE}")
    print("=" * 60 + "\n")

    network_body = None
    network_url  = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(viewport=None)
        page    = await context.new_page()

        # Capturar respuesta de red
        async def on_response(response):
            nonlocal network_body, network_url
            if "inciapi.com/api/web/products" in response.url and BARCODE in response.url:
                network_url = response.url
                try:
                    network_body = await response.json()
                    print(f"[NET] Capturado: {response.url}")
                except Exception:
                    pass

        page.on("response", on_response)

        ok = await do_login(page)
        if not ok:
            print("[ERROR] Login fallo.")
            await browser.close()
            return

        print(f"[->] Navegando al playground...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Detectar input y boton
        async def find(candidates):
            for sel in candidates:
                try:
                    if await page.locator(sel).first.count() > 0:
                        return sel
                except Exception:
                    continue
            return None

        input_sel = await find([
            'input[placeholder*="Código de barras" i]',
            'input[placeholder*="barcode" i]',
            'input[placeholder*="codigo" i]',
            'input[type="search"]', 'input[type="text"]',
            'input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])',
        ])
        button_sel = await find([
            'button:has-text("Analizar producto")',
            'button:has-text("Analizar")',
            'button:has-text("Analyze")',
            'button:has-text("Buscar")',
            'button[type="submit"]', 'button',
        ])

        if not input_sel or not button_sel:
            print("[ERROR] No se encontraron input/boton.")
            await page.screenshot(path=str(BASE_DIR / "sniffer_debug.png"))
            await browser.close()
            return

        print(f"[OK] Input : {input_sel}")
        print(f"[OK] Boton : {button_sel}\n")

        # Buscar el barcode
        print(f"[->] Buscando barcode {BARCODE}...")
        await page.locator(input_sel).first.click(click_count=3)
        await page.locator(input_sel).first.fill(BARCODE)
        await asyncio.sleep(0.3)
        await page.locator(button_sel).first.click()

        # Esperar a que aparezca "Respuesta JSON sin procesar" en el DOM
        print("[->] Esperando que el JS renderice el resultado...")
        dom_json = None
        dom_sel  = None

        for intento in range(10):   # hasta 10s
            await asyncio.sleep(1)
            dom_json, dom_sel = await extract_dom_json(page)
            if dom_json:
                print(f"[OK] JSON encontrado en DOM ({dom_sel}) tras {intento+1}s")
                break
            print(f"     intento {intento+1}/10 — aun no aparece...")

        # Screenshot de como quedo la pagina
        await page.screenshot(path=str(BASE_DIR / "sniffer_resultado.png"))

        # Dump completo del HTML para debugging
        html = await page.content()
        (BASE_DIR / "sniffer_page.html").write_text(html, encoding="utf-8")
        print("[OK] HTML completo guardado: sniffer_page.html")

        await browser.close()

    # ---------------------------------------------------------------------------
    # Guardar resultados
    # ---------------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"  RESULTADOS")
    print(f"{'='*60}\n")

    resultado = {
        "barcode"          : BARCODE,
        "network_endpoint" : network_url,
        "network_body"     : network_body,
        "dom_json"         : dom_json,
        "dom_selector"     : dom_sel,
    }

    print(f"  Red   → {network_url}")
    if network_body:
        print(f"          keys: {list(network_body.keys())}")

    if dom_json:
        print(f"  DOM   → encontrado con selector '{dom_sel}'")
        print(f"          keys: {list(dom_json.keys())}")
    else:
        print(f"  DOM   → NO encontrado")
        print(f"          Revisa sniffer_page.html para ver el HTML completo")
        print(f"          y sniffer_resultado.png para ver la pantalla")

    OUTPUT_JSON.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n[OK] Guardado en {OUTPUT_JSON.name}")


if __name__ == "__main__":
    asyncio.run(main())
