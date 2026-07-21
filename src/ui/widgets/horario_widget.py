"""
src/ui/widgets/horario_widget.py
=================================
Widget de solo lectura que dibuja el horario semanal de los grupos asignados
a las materias de un semestre, en forma de rejilla Hora × Día.

Recibe el diccionario código→grupo que arma
`planner_service.generar_plan_personalizado` y pinta cada sesión en su franja
horaria con un color distinto por materia.
"""

from __future__ import annotations
import customtkinter as ctk
from src.config.theme import COLORES, FUENTE_PEQUEÑA, FUENTE_NORMAL

_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

# Paleta cíclica para diferenciar materias en la rejilla; no usa COLORES del
# theme porque aquí se necesita contraste variado entre materias, no jerarquía.
_PALETA = [
    "#7c6fff",
    "#10d9a0",
    "#f59e0b",
    "#ef4444",
    "#3b82f6",
    "#ec4899",
    "#22c55e",
    "#a855f7",
    "#eab308",
    "#06b6d4",
]


class HorarioWidget(ctk.CTkFrame):
    """
    Rejilla visual de horario semanal para un semestre.

    Parámetros:
        parent: Widget contenedor.
        asignacion (dict[str, dict]): código de materia → grupo asignado (con "sessions").
        materias_perfil (dict): diccionario código→datos de materia, para el nombre.
        hora_inicio / hora_fin (int): rango de horas a dibujar (24h, fin exclusivo).
    """

    def __init__(
        self,
        parent,
        asignacion: dict[str, dict],
        materias_perfil: dict,
        hora_inicio: int = 6,
        hora_fin: int = 19,
        **kwargs,
    ) -> None:
        super().__init__(
            parent, fg_color=COLORES["bg_card"], corner_radius=10, **kwargs
        )
        self._colores_materia = self._asignar_colores(asignacion)
        self._construir(asignacion, materias_perfil, hora_inicio, hora_fin)

    def _asignar_colores(self, asignacion: dict[str, dict]) -> dict[str, str]:
        return {
            cod: _PALETA[i % len(_PALETA)]
            for i, cod in enumerate(sorted(asignacion.keys()))
        }

    def _construir(self, asignacion, materias_perfil, hora_inicio, hora_fin) -> None:
        if not asignacion:
            ctk.CTkLabel(
                self,
                text="Sin información de horario para este semestre.",
                font=FUENTE_PEQUEÑA,
                text_color=COLORES["text_muted"],
            ).pack(padx=16, pady=16)
            return

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=10)

        grid.grid_columnconfigure(0, weight=0, minsize=70)
        for c, dia in enumerate(_DIAS, start=1):
            grid.grid_columnconfigure(c, weight=1, minsize=140)
            ctk.CTkLabel(
                grid,
                text=dia,
                font=FUENTE_NORMAL,
                text_color=COLORES["text_primary"],
            ).grid(row=0, column=c, sticky="nsew", padx=2, pady=2)

        # Sesiones por día, ya con nombre/color/grupo resueltos.
        ocupacion: dict[str, list[dict]] = {d: [] for d in _DIAS}
        for cod, grupo in asignacion.items():
            nombre = grupo.get("materia_nombre") or materias_perfil.get(cod, {}).get(
                "nombre", cod
            )
            color = self._colores_materia[cod]
            for sesion in grupo.get("sessions", []):
                dia = sesion.get("day")
                if dia in ocupacion:
                    ocupacion[dia].append(
                        {
                            "inicio": sesion.get("beginHour"),
                            "fin": sesion.get("endHour"),
                            "aula": sesion.get("classroom", ""),
                            "nombre": nombre,
                            "color": color,
                            "grupo": grupo.get("code", ""),
                        }
                    )

        for i, hora in enumerate(range(hora_inicio, hora_fin), start=1):
            ctk.CTkLabel(
                grid,
                text=f"{hora:02d}:00 - {(hora+1):02d}:00",
                font=FUENTE_PEQUEÑA,
                text_color=COLORES["text_muted"],
            ).grid(row=i, column=0, sticky="nsew", padx=2, pady=1)

            for c, dia in enumerate(_DIAS, start=1):
                celda = next(
                    (
                        s
                        for s in ocupacion[dia]
                        if s["inicio"] is not None and s["inicio"] <= hora < s["fin"]
                    ),
                    None,
                )
                marco = ctk.CTkFrame(
                    grid,
                    fg_color=celda["color"] if celda else COLORES["bg_deep"],
                    corner_radius=4,
                    height=34,
                )
                marco.grid(row=i, column=c, sticky="nsew", padx=2, pady=1)
                if celda:
                    texto = celda["nombre"]
                    if celda["grupo"] or celda["aula"]:
                        texto += f"\n{celda['grupo']}  ·  {celda['aula']}"
                    ctk.CTkLabel(
                        marco,
                        text=texto,
                        font=FUENTE_PEQUEÑA,
                        text_color="#0d0f1a",
                        justify="left",
                    ).pack(padx=4, pady=2, anchor="w")
