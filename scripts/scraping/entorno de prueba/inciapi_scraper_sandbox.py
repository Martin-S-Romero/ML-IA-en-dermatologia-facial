#!/usr/bin/env python3
"""
inciapi_scraper_sandbox.py
- Login automatico en https://inciapi.com/login
- Consulta via https://inciapi.com/dashboard/playground
- Campo "Codigo de barras" + boton "Analizar producto"
- Captura respuesta de red con campo 'endpoint'
- Re-login automatico si la sesion expira
"""

import asyncio
import csv
import json
import random
import time
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent
CSV_FILE    = BASE_DIR.parent / "en.openbeautyfacts.org.products.csv"
OUTPUT_FILE = BASE_DIR / "inci_results.jsonl"
TARGET_URL  = "https://inciapi.com/dashboard/playground"
LOGIN_URL   = "https://inciapi.com/login"

LOGIN_EMAIL = "sheens0graviti+inciapi@gmail.com"
LOGIN_PASS  = "64544249"

DELAY_MIN = 0.5
DELAY_MAX = 1.0

# ---------------------------------------------------------------------------
# Archivos
# ---------------------------------------------------------------------------

def load_barcodes():
    barcodes = []
    with open(CSV_FILE, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row and row[0].strip():
                barcodes.append(row[0].strip())
    return barcodes


def load_done():
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
                obj  = json.loads(line)
                bc   = obj.get("barcode", "")
                data = obj.get("data", {})
                if not isinstance(data, dict):
                    done_err.add(bc)
                elif "product" in data:
                    done_ok.add(bc)
                elif data.get("statusCode") == 404 or data.get("error") == "Not Found":
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


def append_result(barcode: str, data, endpoint: str = None):
    record = {"barcode": barcode}
    if endpoint is not None:
        record["endpoint"] = endpoint
    record["data"] = data
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


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
    """Login automatico. Devuelve True si tuvo exito."""
    print("\n[LOGIN] Iniciando sesion automatica...")
    await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(1)

    email_sel = None
    for sel in ['input[type="email"]', 'input[name*="email" i]',
                'input[placeholder*="email" i]', 'input[placeholder*="correo" i]',
                'input[type="text"]']:
        try:
            if await page.locator(sel).first.count() > 0:
                email_sel = sel
                break
        except Exception:
            continue

    pass_sel = None
    for sel in ['input[type="password"]', 'input[name*="pass" i]',
                'input[placeholder*="contrase" i]', 'input[placeholder*="pass" i]']:
        try:
            if await page.locator(sel).first.count() > 0:
                pass_sel = sel
                break
        except Exception:
            continue

    if not email_sel or not pass_sel:
        print("[LOGIN] Campos no encontrados. Screenshot guardado.")
        await page.screenshot(path=str(BASE_DIR / "inci_login_debug.png"))
        return False

    await page.locator(email_sel).first.fill(LOGIN_EMAIL)
    await asyncio.sleep(0.3)
    await page.locator(pass_sel).first.fill(LOGIN_PASS)
    await asyncio.sleep(0.3)

    submit_sel = None
    for sel in ['button[type="submit"]', 'button:has-text("Iniciar sesión")',
                'button:has-text("Iniciar")', 'button:has-text("Login")',
                'button:has-text("Entrar")', 'button']:
        try:
            if await page.locator(sel).first.count() > 0:
                submit_sel = sel
                break
        except Exception:
            continue

    if submit_sel:
        await page.locator(submit_sel).first.click()
    else:
        await page.locator(pass_sel).first.press("Enter")

    try:
        await page.wait_for_url(
            lambda url: "login" not in url.lower(),
            timeout=15000
        )
        print("[LOGIN] Sesion iniciada. Navegando al playground...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(1.5)
        return True
    except PlaywrightTimeout:
        print("[LOGIN] Timeout. Screenshot guardado.")
        await page.screenshot(path=str(BASE_DIR / "inci_login_debug.png"))
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    all_barcodes = load_barcodes()
    done_ok, done_err = load_done()

    if done_err:
        print(f"[INFO] {len(done_err)} barcodes con errores seran reintentados.")
        rewrite_jsonl_without(done_err)

    pending = [bc for bc in all_barcodes if bc not in done_ok]

    print(f"\n{'='*60}")
    print(f"  Total en CSV    : {len(all_barcodes):,}")
    print(f"  Con resultado OK: {len(done_ok):,}")
    print(f"  A reintentar    : {len(done_err):,}")
    print(f"  Pendientes total: {len(pending):,}")
    print(f"{'='*60}\n")

    if not pending:
        print("[OK] Todos los codigos ya fueron procesados!")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(viewport=None)
        page    = await context.new_page()

        # Login automatico al arrancar
        ok = await do_login(page)
        if not ok:
            print("\n[ERROR] Login fallo. Revisa inci_login_debug.png.")
            await browser.close()
            return

        print(f"[OK] Pagina: {page.url}")
        await page.screenshot(path=str(BASE_DIR / "inci_debug.png"))

        # Detectar selectores
        print("\n[->] Detectando elementos del playground...")

        input_sel = await find_selector(page, [
            'input[placeholder*="Código de barras" i]',
            'input[placeholder*="codigo de barras" i]',
            'input[placeholder*="barcode" i]',
            'input[placeholder*="codigo" i]',
            'input[type="search"]',
            'input[type="text"]',
            'input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])',
        ])
        if not input_sel:
            print("[ERROR] No se encontro el input. Revisa inci_debug.png.")
            await browser.close()
            return
        print(f"[OK] Input : {input_sel}")

        button_sel = await find_selector(page, [
            'button:has-text("Analizar producto")',
            'button:has-text("Analizar")',
            'button:has-text("analizar")',
            'button:has-text("Analyze")',
            'button:has-text("Buscar")',
            'button[type="submit"]',
            'button',
        ])
        if not button_sel:
            print("[ERROR] No se encontro el boton.")
            await browser.close()
            return
        print(f"[OK] Boton : {button_sel}")

        # ------------------------------------------------------------------
        # Loop principal
        # ------------------------------------------------------------------
        print(f"\n[->] Procesando {len(pending):,} codigos...\n")

        done       = 0
        errors_row = 0
        start_time = time.time()

        for barcode in pending:
            if done % 50 == 0:
                elapsed = time.time() - start_time
                rate    = done / elapsed if elapsed > 0 else 0
                eta_min = (len(pending) - done) / rate / 60 if rate > 0 else float("inf")
                print(f"  [{done:>6}/{len(pending):,}] {barcode}  "
                      f"| {rate:.1f} req/s | ETA: {eta_min:.0f} min")

            try:
                if await is_session_expired(page):
                    ok = await do_login(page)
                    if not ok:
                        print("[!] Re-login fallo. Pausa 60s...")
                        await asyncio.sleep(60)
                        continue

                await page.locator(input_sel).first.click(click_count=3)
                await page.locator(input_sel).first.fill(barcode)
                await asyncio.sleep(0.2)

                try:
                    async with page.expect_response(
                        lambda r: "inciapi.com" in r.url
                                  and r.url != TARGET_URL
                                  and r.status in (200, 404, 400, 401, 403, 422),
                        timeout=12000
                    ) as resp_info:
                        await page.locator(button_sel).first.click()

                    resp     = await resp_info.value
                    endpoint = resp.url

                    if resp.status in (401, 403):
                        print(f"\n[!] Sesion expirada (HTTP {resp.status}), relogueando...")
                        ok = await do_login(page)
                        if ok:
                            async with page.expect_response(
                                lambda r: "inciapi.com" in r.url
                                          and r.url != TARGET_URL
                                          and r.status in (200, 404, 400, 422),
                                timeout=12000
                            ) as resp_info2:
                                await page.locator(input_sel).first.click(click_count=3)
                                await page.locator(input_sel).first.fill(barcode)
                                await page.locator(button_sel).first.click()
                            resp     = await resp_info2.value
                            endpoint = resp.url
                        else:
                            append_result(barcode, {"error": "session_expired"})
                            done += 1
                            continue

                    try:
                        data = await resp.json()
                    except Exception:
                        data = {"raw": await resp.text()}

                    append_result(barcode, data, endpoint)
                    errors_row = 0

                except PlaywrightTimeout:
                    if await is_session_expired(page):
                        ok = await do_login(page)
                        if not ok:
                            append_result(barcode, {"error": "session_expired"})
                            done += 1
                            continue
                        continue
                    else:
                        append_result(barcode, {"error": "no_network_response"})
                        errors_row += 1

                done += 1
                await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

                if errors_row >= 10:
                    print("[!] 10 timeouts seguidos, pausando 30s...")
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
