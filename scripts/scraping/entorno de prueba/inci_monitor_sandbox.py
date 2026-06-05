#!/usr/bin/env python3
"""
inci_monitor.py  -  Monitor en tiempo real de inci_results.jsonl
Ejecutar en una CMD separada mientras corre el scraper.
"""

import json
import time
import os
from pathlib import Path

BASE_DIR      = Path(__file__).parent
CSV_FILE      = BASE_DIR / "en.openbeautyfacts.org.products.csv"
RESULTS_FILE  = BASE_DIR / "inci_results.jsonl"

REFRESH_SEC = 1  # segundos entre actualizaciones


def load_csv_total():
    """Cuenta barcodes unicos no vacios del CSV."""
    import csv
    barcodes = set()
    try:
        with open(CSV_FILE, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row and row[0].strip():
                    barcodes.add(row[0].strip())
    except Exception:
        pass
    return len(barcodes)


def count_results():
    con_datos = 0   # tiene campo "product" en data
    sin_datos = 0   # 404 del API (producto no encontrado)
    errores   = 0   # fallo del scraper (timeout, red, etc.)

    if not RESULTS_FILE.exists():
        return 0, 0, 0

    with open(RESULTS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj  = json.loads(line)
                data = obj.get("data", {})

                if not isinstance(data, dict):
                    errores += 1
                elif "product" in data:
                    con_datos += 1
                elif data.get("statusCode") == 404 or data.get("error") == "Not Found":
                    sin_datos += 1
                elif "error" in data:
                    errores += 1
                else:
                    errores += 1
            except Exception:
                errores += 1

    return con_datos, sin_datos, errores


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def bar(value, total, width=40):
    filled = int(width * value / total) if total > 0 else 0
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main():
    print("Cargando CSV para contar total... ", end="", flush=True)
    csv_total = load_csv_total()
    print(f"{csv_total:,} barcodes unicos.\n")
    print("Iniciando monitor... (Ctrl+C para salir)\n")

    start = time.time()
    prev_total = 0
    speed_samples = []

    try:
        while True:
            con_datos, sin_datos, errores = count_results()
            total_procesados = con_datos + sin_datos + errores
            pendientes = csv_total - total_procesados

            # Velocidad (req/min, ventana 60s)
            now     = time.time()
            elapsed = now - start
            if total_procesados > prev_total:
                speed_samples.append((now, total_procesados - prev_total))
                speed_samples = [(t, d) for t, d in speed_samples if now - t < 60]
                prev_total = total_procesados

            reqs_last_min = sum(d for _, d in speed_samples)
            eta_min = (pendientes / reqs_last_min) if reqs_last_min > 0 else float("inf")
            pct = (total_procesados / csv_total * 100) if csv_total > 0 else 0

            clear()
            print("=" * 55)
            print("   INCI SCRAPER  -  Monitor en tiempo real")
            print("=" * 55)
            print(f"  Progreso      : {bar(total_procesados, csv_total)}")
            print(f"                  {total_procesados:,} / {csv_total:,}  ({pct:.1f}%)")
            print()
            print(f"  Con datos     : {con_datos:,}")
            print(f"  Sin datos (404): {sin_datos:,}")
            print(f"  Errores scraper: {errores:,}")
            print(f"  Pendientes    : {pendientes:,}")
            print()
            print(f"  Velocidad     : {reqs_last_min:.0f} req/min (ultima ventana de 60s)")
            if reqs_last_min > 0:
                print(f"  ETA           : {eta_min:.0f} min  ({eta_min/60:.1f} h)")
            else:
                print(f"  ETA           : --")
            print()
            print(f"  Corriendo hace: {elapsed/60:.1f} min")
            print(f"  Actualiza cada: {REFRESH_SEC}s  |  Ctrl+C para salir")
            print("=" * 55)

            time.sleep(REFRESH_SEC)

    except KeyboardInterrupt:
        print("\n\n[OK] Monitor cerrado.")


if __name__ == "__main__":
    main()
