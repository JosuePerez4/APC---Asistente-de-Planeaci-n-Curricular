"""
tools/scrape_pensum.py
======================
CLI que extrae el plan de estudios desde el HTML del portal universitario y lo
vuelca a un JSON neutro.

La lógica de parseo vive en `src/services/pensum_parser.py`, compartida con el
diálogo de importación de la app. Este módulo es solo la envoltura de línea de
comandos: argumentos, I/O y resumen.

Uso:
    python tools/scrape_pensum.py data/pensum.html -o data/pensum.json

El HTML se obtiene en el portal con la sesión abierta: F12 → clic derecho
sobre la <table> del pénsum → Copy → Copy outerHTML.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Permite ejecutar el script directamente (`python tools/scrape_pensum.py`)
# sin instalar el paquete: añade la raíz del repo al path de importación.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.pensum_parser import APROBADA, PENDIENTE, parse_pensum  # noqa: E402

# Claves que se serializan al JSON. "avisos" se reporta por stderr, no se
# escribe al archivo: es diagnóstico de la corrida, no parte del pénsum.
_CLAVES_SALIDA = ("materias", "electivas")


def _resumen(pensum: dict) -> None:
    """Imprime a stderr un resumen de lo extraído y los avisos encontrados."""
    materias, electivas = pensum["materias"], pensum["electivas"]
    todas = materias + electivas
    estados = Counter(m["estado"] for m in todas)
    semestres = {m["semestre"] for m in todas}

    for aviso in pensum["avisos"]:
        print(f"  ! aviso: {aviso}", file=sys.stderr)

    print(
        f"\n{len(todas)} materias en {len(semestres)} semestres "
        f"({len(materias)} obligatorias, {len(electivas)} electivas)\n"
        f"  aprobadas: {estados[APROBADA]}   pendientes: {estados[PENDIENTE]}",
        file=sys.stderr,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[3])
    parser.add_argument("html", help="Archivo HTML del pénsum guardado desde el portal")
    parser.add_argument("-o", "--output", default="data/pensum.json",
                        help="Ruta del JSON de salida (por defecto: data/pensum.json)")
    args = parser.parse_args()

    with open(args.html, encoding="utf-8") as f:
        pensum = parse_pensum(f.read())

    if not pensum["materias"] and not pensum["electivas"]:
        print("error: no se encontró ninguna materia; ¿el HTML contiene la tabla del pénsum?",
              file=sys.stderr)
        return 1

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({k: pensum[k] for k in _CLAVES_SALIDA}, f, ensure_ascii=False, indent=2)

    _resumen(pensum)
    print(f"\nEscrito en {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
