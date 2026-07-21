"""
src/models/perfil.py
====================
Modelo de datos del perfil de un estudiante.

Encapsula el nombre, el conjunto de materias aprobadas/vistas y
la preferencia de incluir o no el Proyecto de Grado en el plan.
El formato de serialización es 100 % compatible con el JSON existente
(perfiles_estudios.json), garantizando que el perfil de Daniel
y cualquier otro perfil previo se carguen sin modificación.
"""

from __future__ import annotations
from datetime import datetime


class PerfilEstudiante:
    """
    Representa un perfil de estudiante con su historial académico.

    Atributos:
        nombre (str): Nombre identificador del perfil.
        materias_vistas (set[str]): Conjunto de códigos de materias aprobadas.
        fecha_creacion (str): ISO timestamp de creación del perfil.
        fecha_actualizacion (str): ISO timestamp de la última modificación.
        incluir_proyecto_grado (bool): Si True, el plan incluirá Proyecto de Grado.
    """

    def __init__(
        self,
        nombre: str,
        materias_vistas: list[str] | None = None,
        fecha_creacion: str | None = None,
        incluir_proyecto_grado: bool = True,
        materias_manuales: dict[str, int] | None = None,
    ) -> None:
        self.nombre = nombre
        self.materias_vistas: set[str] = (
            set(materias_vistas) if materias_vistas else set()
        )
        self.fecha_creacion: str = fecha_creacion or datetime.now().isoformat()
        self.fecha_actualizacion: str = datetime.now().isoformat()
        self.incluir_proyecto_grado: bool = incluir_proyecto_grado
        self.materias_manuales: dict[str, int] = materias_manuales or {}

    # ── Serialización ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Convierte el perfil a un diccionario serializable en JSON.
        Mantiene exactamente las mismas claves del archivo perfiles_estudios.json.
        """
        return {
            "nombre": self.nombre,
            "materias_vistas": list(self.materias_vistas),
            "fecha_creacion": self.fecha_creacion,
            "fecha_actualizacion": self.fecha_actualizacion,
            "incluir_proyecto_grado": self.incluir_proyecto_grado,
            "materias_manuales": self.materias_manuales,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PerfilEstudiante":
        """
        Construye un PerfilEstudiante desde un diccionario (leído del JSON).
        Compatible con el formato existente de perfiles_estudios.json.
        """
        perfil = cls(
            nombre=data["nombre"],
            materias_vistas=data.get("materias_vistas", []),
            fecha_creacion=data.get("fecha_creacion"),
            incluir_proyecto_grado=data.get("incluir_proyecto_grado", True),
            materias_manuales=data.get("materias_manuales", {}),
        )
        # Restaurar la fecha de actualización original (no la de ahora)
        perfil.fecha_actualizacion = data.get(
            "fecha_actualizacion", perfil.fecha_creacion
        )
        return perfil

    def __repr__(self) -> str:
        return (
            f"PerfilEstudiante(nombre={self.nombre!r}, "
            f"materias_vistas={len(self.materias_vistas)}, "
            f"proyecto_grado={self.incluir_proyecto_grado}, "
            f"materias_manuales={len(self.materias_manuales)})"
        )
