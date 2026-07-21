"""
src/ui/widgets/materia_editor_row.py
======================================
Widget interactivo con checkbox para el editor de materias vistas.

Muestra el código, nombre, créditos y prerequisitos de una materia junto
con un checkbox que indica si el estudiante la ha cursado. El badge de
estado (Vista / Pendiente) refleja el valor inicial del checkbox.
"""

from __future__ import annotations
import customtkinter as ctk
from src.config.theme import COLORES, FUENTE_H2, FUENTE_NORMAL, FUENTE_PEQUEÑA, GLYPHS


class MateriaEditorRow(ctk.CTkFrame):
    """
    Fila interactiva con checkbox para marcar una materia como vista en el editor.

    Parámetros:
        parent: Widget contenedor.
        codigo (str): Código único de la materia.
        materia (dict): Datos de la materia (nombre, creditos, prereq).
        is_checked (bool): Estado inicial del checkbox.
        on_toggle (callable): Callback invocado con (codigo, BooleanVar) al cambiar.
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        codigo: str,
        materia: dict,
        is_checked: bool,
        on_toggle,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=COLORES["bg_card"],
            corner_radius=8,
            **kwargs,
        )
        self.codigo = codigo
        self.var = ctk.BooleanVar(value=is_checked)
        self._construir(codigo, materia, is_checked, on_toggle)

    def _construir(
        self, codigo: str, materia: dict, is_checked: bool, on_toggle
    ) -> None:
        """Construye el layout interno de la fila."""

        # ── Checkbox ──────────────────────────────────────────────────────
        ctk.CTkCheckBox(
            self,
            text="",
            variable=self.var,
            command=lambda: on_toggle(self.codigo, self.var),
            width=20,
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            checkmark_color=COLORES["text_primary"],
            border_color=COLORES["border_subtle"],
        ).pack(side="left", padx=14, pady=12)

        # ── Info frame ────────────────────────────────────────────────────
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        # Fila superior: código + badge de estado
        fila_top = ctk.CTkFrame(info, fg_color="transparent")
        fila_top.pack(fill="x")

        ctk.CTkLabel(
            fila_top,
            text=f"{GLYPHS['memo']}  {codigo}",
            font=FUENTE_H2,
            text_color=COLORES["accent_primary"],
            anchor="w",
        ).pack(side="left")

        # Badge de estado (basado en el valor inicial)
        badge_color = COLORES["accent_success"] if is_checked else COLORES["bg_hover"]
        badge_text = f"{GLYPHS['check']} Vista" if is_checked else "Pendiente"
        badge = ctk.CTkFrame(fila_top, fg_color=badge_color, corner_radius=6)
        badge.pack(side="right", padx=(0, 6))
        ctk.CTkLabel(
            badge,
            text=f"  {badge_text}  ",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_primary"],
        ).pack(padx=2, pady=2)

        # Nombre de la materia
        ctk.CTkLabel(
            info,
            text=materia["nombre"],
            font=FUENTE_NORMAL,
            text_color=COLORES["text_primary"],
            wraplength=650,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Detalles: créditos y prerequisitos
        detalles = ctk.CTkFrame(info, fg_color="transparent")
        detalles.pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            detalles,
            text=f"{GLYPHS['target']}  {materia['creditos']} créditos",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_muted"],
        ).pack(side="left", padx=(0, 14))

        if materia["prereq"]:
            prereq_text = f"{GLYPHS['link']}  {', '.join(materia['prereq'])}"
            prereq_color = COLORES["accent_warning"]
        else:
            prereq_text = f"{GLYPHS['check']}  Sin prereqs"
            prereq_color = COLORES["accent_success"]

        ctk.CTkLabel(
            detalles,
            text=prereq_text,
            font=FUENTE_PEQUEÑA,
            text_color=prereq_color,
        ).pack(side="left")
