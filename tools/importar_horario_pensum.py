"""
tools/importar_horario_pensum.py
=================================
CLI que consulta el pénsum vigente (materias, prerrequisitos y horarios de
grupos ofertados) desde la API del portal y lo guarda en data/pensum_horarios.json.

Es la fuente de datos que consume `src/config/pensum_data.py` en vez del plan
curricular hardcodeado en `curriculum.py`. Se ejecuta manualmente o desde el
botón "Regenerar Pénsum" en la pantalla de perfiles, cada vez que cambian los
horarios ofertados del periodo.

ADVERTENCIA: el token de autenticación es personal e intransferible y expira
en poco tiempo (es un JWT de sesión, no una API key). No lo dejes hardcodeado
ni lo subas a un repositorio: pásalo por variable de entorno o argumento.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
_OUTPUT_FILE = _RAIZ_PROYECTO / "data" / "pensum_horarios.json"
_URL = "https://horarioapp.0025600.xyz/pensum"


def _transformar(data: dict) -> dict:
    """Conserva solo los campos que usa la app (ver `pensum_data.py`)."""
    transformado = {"subjects": []}

    for subject in data.get("subjects", []):
        nueva = {
            "id": subject.get("id"),
            "code": subject.get("code"),
            "name": subject.get("name"),
            "credits": subject.get("credits"),
            "semester": subject.get("semester"),
            "requiredCredits": subject.get("requiredCredits"),
            "type": subject.get("type"),
            "requisites": [
                {"id": r.get("id"), "name": r.get("name"), "code": r.get("code")}
                for r in subject.get("requisites", [])
            ],
            "groups": [],
        }

        for group in subject.get("groups", []):
            nuevo_grupo = {
                "id": group.get("id"),
                "code": group.get("code"),
                "teacher": group.get("teacher"),
                "program": group.get("program"),
                "maxCapacity": group.get("maxCapacity"),
                "availableCapacity": group.get("availableCapacity"),
                "sessions": [
                    {
                        "id": s.get("id"),
                        "day": s.get("day"),
                        "beginHour": s.get("beginHour"),
                        "endHour": s.get("endHour"),
                        "classroom": s.get("classroom"),
                    }
                    for s in group.get("sessions", [])
                ],
            }
            nueva["groups"].append(nuevo_grupo)

        transformado["subjects"].append(nueva)

    return transformado


def obtener_pensum(token: str) -> dict | None:
    """Consulta la API y devuelve el pénsum ya filtrado, o None si falla."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        respuesta = requests.get(_URL, headers=headers, timeout=20)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"error en la petición: {exc}", file=sys.stderr)
        return None
    return _transformar(respuesta.json())


def main() -> int:
    # Orden de prioridad para el token: argumento de línea de comandos >
    # variable de entorno APC_TOKEN. Así nunca queda escrito en el archivo.
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("APC_TOKEN")
    if not token:
        print(
            "error: falta el token. Pásalo así:\n"
            "  python tools/importar_horario_pensum.py TU_TOKEN\n"
            "o exporta la variable de entorno APC_TOKEN antes de correr el script.",
            file=sys.stderr,
        )
        return 1

    pensum = obtener_pensum(token)
    if pensum is None:
        return 1

    _OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pensum, f, ensure_ascii=False, indent=2)

    print(
        f"{len(pensum['subjects'])} materias escritas en {_OUTPUT_FILE}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
