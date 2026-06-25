"""
src/services/perfil_service.py
==============================
Servicio de persistencia de perfiles de estudiante.

Responsabilidades:
  - Cargar perfiles desde el archivo JSON.
  - Guardar perfiles en el archivo JSON.

Esta capa NO contiene lógica de UI. Si falla el guardado, lanza
RuntimeError para que la capa de presentación la maneje con un diálogo.

El archivo perfiles_estudios.json se busca siempre en la raíz del proyecto
(directorio padre de `src/`), independientemente del CWD actual.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.models.perfil import PerfilEstudiante

# Ruta absoluta al archivo de perfiles (data/perfiles_estudios.json en raíz del proyecto)
_RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
PROFILES_FILE: Path = _RAIZ_PROYECTO / "data" / "perfiles_estudios.json"


def cargar_perfiles() -> dict[str, PerfilEstudiante]:
    """
    Lee el archivo JSON de perfiles y retorna un dict nombre → PerfilEstudiante.
    Si el archivo no existe o está corrupto, retorna un dict vacío y lo reporta en consola.
    """
    if not PROFILES_FILE.exists():
        return {}

    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            datos: dict = json.load(f)
        return {
            nombre: PerfilEstudiante.from_dict(perfil_data)
            for nombre, perfil_data in datos.items()
        }
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"[APC] Error al cargar perfiles desde '{PROFILES_FILE}': {exc}")
        return {}


def guardar_perfiles(perfiles: dict[str, PerfilEstudiante]) -> None:
    """
    Serializa y escribe todos los perfiles en el archivo JSON.

    Raises:
        RuntimeError: Si la escritura falla (permisos, disco lleno, etc.).
                      La capa de UI debe capturar este error y mostrarlo al usuario.
    """
    try:
        # Asegurar que el directorio de datos existe
        PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        datos = {nombre: perfil.to_dict() for nombre, perfil in perfiles.items()}
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise RuntimeError(
            f"No se pudieron guardar los perfiles en '{PROFILES_FILE}':\n{exc}"
        ) from exc
