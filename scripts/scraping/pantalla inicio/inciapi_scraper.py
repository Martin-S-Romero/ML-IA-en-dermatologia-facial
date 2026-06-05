#!/usr/bin/env python3
"""
inciapi_scraper.py
- Consulta directamente https://inciapi.com/api/web/demo/products/{barcode}
- Sin browser — requests HTTP async con aiohttp
- CONCURRENCY requests en paralelo
- Guarda en inci_results.jsonl con campo 'endpoint'
"""

import asyncio
import csv
import json
import random
import time
from pathlib import Path
import aiohttp

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent
CSV_FILE    = BASE_DIR / "en.openbeautyfacts.org.products.csv"
OUTPUT_FILE = BASE_DIR / "inci_results.jsonl"
API_BASE    = "https://inciapi.com/api/web/demo/products"

CONCURRENCY = 15     # requests en paralelo
DELAY_MIN   = 0.1
DELAY_MAX   = 0.2

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
    """
    done_ok  : barcodes con respuesta real (product o 404) -> no reintentar
    done_err : barcodes con error de red/scraper           -> reintentar
    """
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
# Worker
# ---------------------------------------------------------------------------

async def fetch_barcode(session: aiohttp.ClientSession, semaphore: asyncio.Semaphore,
                        barcode: str, progress: dict):
    url = f"{API_BASE}/{barcode}"
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                endpoint = str(resp.url)

                # Rate limit — esperar y reintentar una vez
                if resp.status == 429:
                    print(f"\n[429] Rate limit. Pausando 30s...")
                    await asyncio.sleep(30)
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        endpoint = str(resp.url)
                        try:
                            data = await resp.json(content_type=None)
                        except Exception:
                            data = {"raw": await resp.text()}
                else:
                    try:
                        data = await resp.json(content_type=None)
                    except Exception:
                        data = {"raw": await resp.text()}

                append_result(barcode, data, endpoint)

        except asyncio.TimeoutError:
            append_result(barcode, {"error": "timeout"})
        except Exception as e:
            append_result(barcode, {"error": str(e)})

        # Progreso
        progress["done"] += 1
        done  = progress["done"]
        total = progress["total"]
        if done % 50 == 0:
            elapsed = time.time() - progress["start"]
            rate    = done / elapsed if elapsed > 0 else 0
            eta_min = (total - done) / rate / 60 if rate > 0 else float("inf")
            print(f"  [{done:>6}/{total:,}] {barcode}  | {rate:.1f} req/s | ETA: {eta_min:.0f} min")

        await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


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
    print(f"  Concurrencia    : {CONCURRENCY} requests en paralelo")
    print(f"{'='*60}\n")

    if not pending:
        print("[OK] Todos los codigos ya fueron procesados!")
        return

    progress = {"done": 0, "total": len(pending), "start": time.time()}
    semaphore = asyncio.Semaphore(CONCURRENCY)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    print(f"[->] Iniciando {len(pending):,} requests a {API_BASE}/...\n")

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            fetch_barcode(session, semaphore, bc, progress)
            for bc in pending
        ]
        await asyncio.gather(*tasks)

    elapsed = time.time() - progress["start"]
    print(f"\n{'='*60}")
    print(f"  Procesados  : {progress['done']:,}")
    print(f"  Tiempo total: {elapsed/60:.1f} min")
    print(f"  Resultado   : {OUTPUT_FILE.name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
