"""
src/ui/views/perfil_view.py
============================
Vista de selección, creación y eliminación de perfiles de estudiante.

Responsabilidades:
  - Mostrar el grid de cards de perfiles existentes con barra de progreso.
  - Permitir crear un nuevo perfil con nombre y preferencia de Proyecto de Grado.
  - Permitir eliminar perfiles con confirmación.
  - Navegar hacia la vista del plan al seleccionar un perfil.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import customtkinter as ctk

import subprocess
import sys
from pathlib import Path

from src.config import pensum_data

from src.config.theme import (
    COLORES,
    FUENTE_H1,
    FUENTE_H2,
    FUENTE_NORMAL,
    FUENTE_PEQUEÑA,
    GLYPHS,
)
from src.models.perfil import PerfilEstudiante
from src.services.perfil_service import guardar_perfiles
from src.services.planner_service import obtener_materias_por_perfil
from src.ui.dialogs.custom_messagebox import CustomMessageBox

if TYPE_CHECKING:
    from src.ui.app import PlanEstudiosApp


class PerfilView:
    """
    Pantalla principal de selección de perfiles.

    Muestra cards de perfiles existentes con estadísticas y barra de progreso,
    y un botón para crear nuevos perfiles.
    """

    def __init__(self, parent: ctk.CTkFrame, app: "PlanEstudiosApp") -> None:
        self.parent = parent
        self.app = app
        self._construir()

    # ── Construcción ──────────────────────────────────────────────────────

    def _construir(self) -> None:
        """Construye todos los componentes de la vista."""
        self._construir_header()
        self._construir_area_perfiles()
        self._construir_footer()

    def _construir_header(self) -> None:
        """Header con título y subtítulo de la aplicación."""
        header = ctk.CTkFrame(
            self.parent,
            fg_color=COLORES["bg_elevated"],
            corner_radius=16,
            height=104,
        )
        header.pack(fill="x", pady=(0, 18))
        header.pack_propagate(False)

        # Título principal
        ctk.CTkLabel(
            header,
            text=f"{GLYPHS['cap']}  APC — Asistente de Planeación Curricular",
            font=FUENTE_H1,
            text_color=COLORES["text_primary"],
        ).pack(expand=True, pady=(22, 2))

        # Subtítulo descriptivo
        ctk.CTkLabel(
            header,
            text="Selecciona tu perfil para ver o generar tu plan de estudios personalizado",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_muted"],
        ).pack(pady=(0, 18))

    def _construir_area_perfiles(self) -> None:
        """Área scrollable con el grid de cards de perfiles."""
        self._scroll = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=COLORES["bg_card"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            corner_radius=12,
        )
        self._scroll.pack(fill="both", expand=True)

        if not self.app.perfiles:
            # Estado vacío
            ctk.CTkLabel(
                self._scroll,
                text=f"{GLYPHS['empty']}  No tienes perfiles creados aún.\nHaz clic en '{GLYPHS['sparkles']} Nuevo Perfil' para comenzar.",
                font=FUENTE_NORMAL,
                text_color=COLORES["text_muted"],
                justify="center",
            ).pack(expand=True, pady=60)
            return

        # Encabezado de la sección
        ctk.CTkLabel(
            self._scroll,
            text=f"{GLYPHS['folder']}  Tus perfiles",
            font=FUENTE_H2,
            text_color=COLORES["text_primary"],
            anchor="w",
        ).pack(anchor="w", padx=16, pady=(16, 8))

        # Grid de 2 columnas
        grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grid.pack(fill="x", padx=8, pady=(0, 8))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        for idx, nombre in enumerate(self.app.perfiles):
            fila, col = divmod(idx, 2)
            self._construir_card(grid, nombre, fila, col)

    def _construir_card(
        self, grid: ctk.CTkFrame, nombre: str, fila: int, col: int
    ) -> None:
        """Construye una card individual para un perfil."""
        perfil = self.app.perfiles[nombre]
        materias_p = obtener_materias_por_perfil(perfil)
        total = len(materias_p)
        vistas = len(perfil.materias_vistas)
        porcentaje = vistas / total if total > 0 else 0.0
        fecha = datetime.fromisoformat(perfil.fecha_actualizacion).strftime("%d/%m/%Y")
        proyecto = (
            "Con Proyecto de Grado"
            if perfil.incluir_proyecto_grado
            else "Sin Proyecto de Grado"
        )

        # Marco de la card con borde de acento
        card = ctk.CTkFrame(
            grid,
            fg_color=COLORES["bg_elevated"],
            border_color=COLORES["border_active"],
            border_width=1,
            corner_radius=14,
        )
        card.grid(row=fila, column=col, padx=8, pady=8, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        # Nombre del perfil
        ctk.CTkLabel(
            inner,
            text=f"{GLYPHS['user']}  {nombre}",
            font=FUENTE_H2,
            text_color=COLORES["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        # Metadata: fecha y tipo de plan
        ctk.CTkLabel(
            inner,
            text=f"{GLYPHS['calendar']}  {fecha}   ·   {GLYPHS['cap']}  {proyecto}",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_muted"],
            anchor="w",
        ).pack(anchor="w", pady=(4, 8))

        # Progreso textual
        ctk.CTkLabel(
            inner,
            text=f"Progreso: {vistas}/{total} materias ({porcentaje * 100:.1f}%)",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_secondary"],
            anchor="w",
        ).pack(anchor="w")

        # Barra de progreso visual
        barra = ctk.CTkProgressBar(
            inner,
            fg_color=COLORES["bg_hover"],
            progress_color=COLORES["accent_primary"],
            height=8,
            corner_radius=4,
        )
        barra.pack(fill="x", pady=(4, 14))
        barra.set(porcentaje)

        # Botones de acción
        btns = ctk.CTkFrame(inner, fg_color="transparent")
        btns.pack(fill="x")

        ctk.CTkButton(
            btns,
            text="Seleccionar",
            command=lambda n=nombre: self._seleccionar(n),
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
            font=FUENTE_NORMAL,
            height=36,
            corner_radius=8,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btns,
            text=GLYPHS["trash"],
            command=lambda n=nombre: self._eliminar(n),
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_danger"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_NORMAL,
            width=44,
            height=36,
            corner_radius=8,
        ).pack(side="right")

    def _construir_footer(self) -> None:
        """Footer fijo con botones para crear perfil y regenerar el pénsum."""
        footer = ctk.CTkFrame(self.parent, fg_color="transparent", height=72)
        footer.pack(fill="x", pady=(14, 0))
        footer.pack_propagate(False)

        fila = ctk.CTkFrame(footer, fg_color="transparent")
        fila.pack(fill="both", expand=True, pady=10)

        ctk.CTkButton(
            fila,
            text=f"{GLYPHS['sparkles']}  Nuevo Perfil",
            command=self._crear_perfil,
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
            font=FUENTE_H2,
            height=50,
            corner_radius=12,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            fila,
            text=f"{GLYPHS['import']}  Regenerar Pénsum",
            command=self._regenerar_pensum,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_primary"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_H2,
            height=50,
            corner_radius=12,
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _regenerar_pensum(self) -> None:
        """
        Ejecuta el script que trae los grupos y horarios vigentes del portal y
        recarga `pensum_data` en caliente, sin reiniciar la app.
        """
        token = ctk.CTkInputDialog(
            text=f"{GLYPHS['import']}  Pega tu token de sesión del portal:",
            title="Regenerar Pénsum",
        ).get_input()
        if not token:
            return

        raiz = Path(__file__).resolve().parent.parent.parent.parent
        script = raiz / "tools" / "importar_horario_pensum.py"

        self.app.root.config(cursor="watch")
        self.app.root.update_idletasks()
        try:
            resultado = subprocess.run(
                [sys.executable, str(script), token.strip()],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except Exception as exc:  # noqa: BLE001 — errores de red/proceso son variados
            self.app.root.config(cursor="")
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error",
                message=f"No se pudo ejecutar la actualización:\n{exc}",
            ).get_result()
            return
        self.app.root.config(cursor="")

        if resultado.returncode != 0:
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error al regenerar",
                message=f"El script terminó con errores:\n{resultado.stderr[-400:]}",
            ).get_result()
            return

        pensum_data.recargar()
        CustomMessageBox(
            title=f"{GLYPHS['check']}  Pénsum actualizado",
            message="Se actualizaron las materias y horarios vigentes.",
        ).get_result()
        self.app.mostrar_perfiles()

    # ── Acciones ──────────────────────────────────────────────────────────

    def _seleccionar(self, nombre: str) -> None:
        """Selecciona el perfil y navega al plan de estudios."""
        self.app.perfil_actual = self.app.perfiles[nombre]
        self.app.mostrar_plan()

    def _eliminar(self, nombre: str) -> None:
        """Confirma y elimina un perfil."""
        dialogo = CustomMessageBox(
            title=f"{GLYPHS['warning']}  Confirmar eliminación",
            message=f"¿Eliminar el perfil '{nombre}'?\nEsta acción no se puede deshacer.",
            option_1="Cancelar",
            option_2="Eliminar",
        )
        if dialogo.get_result() != "Eliminar":
            return

        del self.app.perfiles[nombre]
        try:
            guardar_perfiles(self.app.perfiles)
        except RuntimeError as exc:
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error", message=str(exc)
            ).get_result()

        if self.app.perfil_actual and self.app.perfil_actual.nombre == nombre:
            self.app.perfil_actual = None

        # Recargar la vista
        self.app.mostrar_perfiles()

    def _crear_perfil(self) -> None:
        """Solicita nombre y preferencias al usuario para crear un perfil nuevo."""
        # Diálogo de nombre
        dialogo_nombre = ctk.CTkInputDialog(
            text=f"{GLYPHS['user']}  Nombre del nuevo perfil:", title="Nuevo Perfil"
        )
        nombre = dialogo_nombre.get_input()

        if not nombre:
            return

        nombre = nombre.strip()
        if not nombre:
            return

        # Validar duplicado
        if nombre in self.app.perfiles:
            CustomMessageBox(
                title=f"{GLYPHS['warning']}  Nombre duplicado",
                message=f"Ya existe un perfil llamado '{nombre}'.",
            ).get_result()
            return

        # Preferencia de Proyecto de Grado
        dialogo_pg = CustomMessageBox(
            title=f"{GLYPHS['cap']}  Proyecto de Grado",
            message=(
                "¿Incluir Proyecto de Grado en tu plan?\n\n"
                "Sí → el plan incluirá la materia (sem. 10).\n"
                "No → el plan la omitirá."
            ),
            option_1="No",
            option_2="Sí",
        )
        incluir = dialogo_pg.get_result() == "Sí"

        # Crear y persistir
        nuevo = PerfilEstudiante(nombre, incluir_proyecto_grado=incluir)
        self.app.perfiles[nombre] = nuevo
        try:
            guardar_perfiles(self.app.perfiles)
        except RuntimeError as exc:
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error al guardar", message=str(exc)
            ).get_result()

        self.app.perfil_actual = nuevo
        self.app.mostrar_plan()
