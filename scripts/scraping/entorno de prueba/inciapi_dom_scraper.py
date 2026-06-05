#!/usr/bin/env python3
"""
inciapi_dom_scraper.py

Scraper de datos calculados por el cliente (DOM) en /dashboard/playground.
Solo procesa barcodes que ya tienen product data en inci_results.jsonl,
extrayendo el JSON de "Respuesta JSON sin procesar" renderizado por JavaScript.

Output: inci_results_dom.jsonl
  {"barcode": "...", "dom_data": {...}}
"""

import asyncio
import json
import random
import time
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent
SOURCE_JSONL = BASE_DIR / "inci_results.jsonl"          # fuente de barcodes con producto
OUTPUT_FILE  = BASE_DIR / "inci_results_dom.jsonl"      # output de este scraper
TARGET_URL   = "https://inciapi.com/dashboard/playground"
LOGIN_URL    = "https://inciapi.com/login"

LOGIN_EMAIL  = "sheens0graviti+inciapi@gmail.com"
LOGIN_PASS   = "64544249"

DELAY_MIN    = 0.3
DELAY_MAX    = 0.6
DOM_TIMEOUT  = 2     # segundos maximos esperando que el DOM renderice

# ---------------------------------------------------------------------------
# Carga de barcodes fuente
# ---------------------------------------------------------------------------

def load_source_barcodes():
    """Carga barcodes que ya tienen product data en inci_results.jsonl."""
    barcodes = []
    if not SOURCE_JSONL.exists():
        print(f"[ERROR] No existe {SOURCE_JSONL}")
        return barcodes
    with open(SOURCE_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj  = json.loads(line)
                data = obj.get("data") or {}
                if "product" in data:
                    barcodes.append(obj["barcode"])
            except Exception:
                pass
    return barcodes


def load_done_dom():
    """Barcodes ya procesados en inci_results_dom.jsonl."""
    done_ok  = set()
    done_err = set()
    if not OUTPUT_FILE.exists():
        return done_ok, done_err
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                bc  = obj.get("barcode", "")
                if obj.get("dom_data") and "error" not in obj.get("dom_data", {}):
                    done_ok.add(bc)
                else:
                    done_err.add(bc)
            except Exception:
                pass
    return done_ok, done_err


def rewrite_jsonl_without(barcodes_to_remove: set):
    if not OUTPUT_FILE.exists() or not barcodes_to_remove:
        return
    lines = []
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                bc = json.loads(line).get("barcode", "")
                if bc not in barcodes_to_remove:
                    lines.append(line)
            except Exception:
                lines.append(line)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


def append_result(barcode: str, dom_data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"barcode": barcode, "dom_data": dom_data},
                            ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

async def find_selector(page, candidates):
    for sel in candidates:
        try:
            if await page.locator(sel).first.count() > 0:
                return sel
        except Exception:
            continue
    return None


async def is_session_expired(page):
    url = page.url.lower()
    if any(x in url for x in ("login", "signin", "logout")):
        return True
    try:
        if await page.locator('input[type="password"]').first.count() > 0:
            return True
    except Exception:
        pass
    return False


async def do_login(page):
    print("\n[LOGIN] Iniciando sesion...")
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
        print("[LOGIN] Campos no encontrados.")
        await page.screenshot(path=str(BASE_DIR / "dom_login_debug.png"))
        return False

    await page.locator(email_sel).first.fill(LOGIN_EMAIL)
    await asyncio.sleep(0.3)
    await page.locator(pass_sel).first.fill(LOGIN_PASS)
    await asyncio.sleep(0.3)

    submit_sel = None
    for sel in ['button[type="submit"]', 'button:has-text("Iniciar sesión")',
                'button:has-text("Iniciar")', 'button:has-text("Login")', 'button']:
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
        print("[LOGIN] Sesion iniciada.")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(1.5)
        return True
    except PlaywrightTimeout:
        print("[LOGIN] Timeout.")
        await page.screenshot(path=str(BASE_DIR / "dom_login_debug.png"))
        return False


# ---------------------------------------------------------------------------
# Extraccion del DOM
# ---------------------------------------------------------------------------

async def extract_dom_json(page):
    """
    Extrae el JSON de 'Respuesta JSON sin procesar' del DOM.
    Busca en pre/code/divs el texto que contiene overallSafetyScore.
    """
    # Intentar con selectores especificos primero
    for sel in ['pre', 'code', '[class*="json"]', '[class*="raw"]',
                '[class*="response"]', '[class*="result"]', '[class*="output"]']:
        try:
            elements = await page.locator(sel).all()
            for el in elements:
                text = (await el.inner_text()).strip()
                if "overallSafetyScore" in text or "skinCompatibility" in text:
                    # Intentar parsear directo
                    try:
                        return json.loads(text)
                    except Exception:
                        # Extraer el objeto JSON del texto
                        start = text.find("{")
                        end   = text.rfind("}") + 1
                        if start >= 0 and end > start:
                            try:
                                return json.loads(text[start:end])
                            except Exception:
                                pass
        except Exception:
            continue

    # Fallback: buscar en el innerText completo de la pagina
    try:
        full_text = await page.evaluate("() => document.body.innerText")
        idx = full_text.find('"overallSafetyScore"')
        if idx < 0:
            idx = full_text.find('"skinCompatibility"')
        if idx >= 0:
            start = full_text.rfind("{", 0, idx)
            if start >= 0:
                depth, end = 0, start
                for i, ch in enumerate(full_text[start:], start):
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                try:
                    return json.loads(full_text[start:end])
                except Exception:
                    pass
    except Exception:
        pass

    return None


async def wait_for_dom_json(page, timeout_s: int = DOM_TIMEOUT):
    """Espera hasta timeout_s segundos a que aparezca el JSON en el DOM."""
    for _ in range(timeout_s):
        result = await extract_dom_json(page)
        if result:
            return result
        await asyncio.sleep(1)
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    source_barcodes = load_source_barcodes()
    done_ok, done_err = load_done_dom()

    if done_err:
        print(f"[INFO] {len(done_err)} barcodes con error seran reintentados.")
        rewrite_jsonl_without(done_err)

    pending = [bc for bc in source_barcodes if bc not in done_ok]

    print(f"\n{'='*60}")
    print(f"  Barcodes con producto en fuente : {len(source_barcodes):,}")
    print(f"  Ya procesados (DOM ok)          : {len(done_ok):,}")
    print(f"  A reintentar                    : {len(done_err):,}")
    print(f"  Pendientes                      : {len(pending):,}")
    print(f"{'='*60}\n")

    if not pending:
        print("[OK] Todos los barcodes ya tienen DOM data!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(viewport=None)
        page    = await context.new_page()

        # Login inicial
        ok = await do_login(page)
        if not ok:
            print("[ERROR] Login fallo. Revisa dom_login_debug.png.")
            await browser.close()
            return

        # Detectar selectores
        print("\n[->] Detectando selectores del playground...")
        input_sel = await find_selector(page, [
            'input[placeholder*="Código de barras" i]',
            'input[placeholder*="codigo de barras" i]',
            'input[placeholder*="barcode" i]',
            'input[placeholder*="codigo" i]',
            'input[type="search"]', 'input[type="text"]',
            'input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])',
        ])
        button_sel = await find_selector(page, [
            'button:has-text("Analizar producto")',
            'button:has-text("Analizar")',
            'button:has-text("Analyze")',
            'button:has-text("Buscar")',
            'button[type="submit"]', 'button',
        ])

        if not input_sel or not button_sel:
            print("[ERROR] No se encontraron input/boton.")
            await page.screenshot(path=str(BASE_DIR / "dom_debug.png"))
            await browser.close()
            return

        print(f"[OK] Input : {input_sel}")
        print(f"[OK] Boton : {button_sel}\n")

        # ------------------------------------------------------------------
        # Loop
        # ------------------------------------------------------------------
        print(f"[->] Procesando {len(pending):,} barcodes...\n")

        done       = 0
        errors_row = 0
        no_dom_row = 0
        start_time = time.time()

        for barcode in pending:
            if done % 50 == 0 and done > 0:
                elapsed = time.time() - start_time
                rate    = done / elapsed if elapsed > 0 else 0
                eta_min = (len(pending) - done) / rate / 60 if rate > 0 else float("inf")
                print(f"  [{done:>6}/{len(pending):,}] | {rate:.1f} req/s | ETA: {eta_min:.0f} min")

            try:
                # Verificar sesion
                if await is_session_expired(page):
                    ok = await do_login(page)
                    if not ok:
                        print("[!] Re-login fallo. Pausa 60s...")
                        await asyncio.sleep(60)
                        continue

                # Escribir barcode y buscar
                await page.locator(input_sel).first.click(click_count=3)
                await page.locator(input_sel).first.fill(barcode)
                await asyncio.sleep(0.2)
                await page.locator(button_sel).first.click()

                # Esperar DOM
                dom_data = await wait_for_dom_json(page, timeout_s=DOM_TIMEOUT)

                if dom_data:
                    append_result(barcode, dom_data)
                    errors_row = 0
                    no_dom_row = 0
                else:
                    # DOM no renderizo — guardar como error para reintentar
                    append_result(barcode, {"error": "dom_not_found"})
                    no_dom_row += 1
                    if no_dom_row >= 5:
                        print(f"[!] {no_dom_row} barcodes sin DOM seguidos — verificar sesion...")
                        if await is_session_expired(page):
                            await do_login(page)
                        no_dom_row = 0

                done += 1
                await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                if errors_row >= 10:
                    print("[!] 10 errores seguidos, pausando 30s...")
                    await asyncio.sleep(30)
                    errors_row = 0

            except Exception as e:
                errors_row += 1
                print(f"\n[ERR] {barcode}: {e}")
                append_result(barcode, {"error": str(e)})
                done += 1

                if errors_row >= 10:
                    print("[!] 10 errores seguidos, pausando 30s...")
                    await asyncio.sleep(30)
                    errors_row = 0

        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"  Procesados  : {done:,}")
        print(f"  Tiempo total: {elapsed/60:.1f} min")
        print(f"  Resultado   : {OUTPUT_FILE.name}")
        print(f"{'='*60}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
