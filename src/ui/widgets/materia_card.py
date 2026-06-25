"""
src/ui/widgets/materia_card.py
================================
Widget de solo lectura para mostrar una materia en la vista del plan de estudios.

Muestra: código con color de acento, badge de créditos, nombre completo
y prerequisitos. Diseño tipo card con bordes sutiles y tipografía jerarquizada.
"""
from __future__ import annotations
import customtkinter as ctk
from src.config.theme import COLORES, FUENTE_H2, FUENTE_NORMAL, FUENTE_PEQUEÑA, GLYPHS


class MateriaCard(ctk.CTkFrame):
    """
    Card visual de solo lectura para una materia del plan de estudios.

    Parámetros:
        parent: Widget contenedor.
        codigo (str): Código único de la materia.
        materia (dict): Datos de la materia (nombre, creditos, prereq, reqCred).
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        codigo: str,
        materia: dict,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            fg_color=COLORES["bg_elevated"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            corner_radius=10,
            **kwargs,
        )
        self._construir(codigo, materia)

    def _construir(self, codigo: str, materia: dict) -> None:
        """Construye el layout interno de la card."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=16, pady=12)

        # ── Fila superior: código y badge de créditos ─────────────────────
        fila_top = ctk.CTkFrame(frame, fg_color="transparent")
        fila_top.pack(fill="x")

        ctk.CTkLabel(
            fila_top,
            text=f"{GLYPHS['memo']}  {codigo}",
            font=FUENTE_H2,
            text_color=COLORES["accent_primary"],
            anchor="w",
        ).pack(side="left")

        # Badge de créditos
        badge = ctk.CTkFrame(
            fila_top,
            fg_color=COLORES["accent_primary"],
            corner_radius=8,
        )
        badge.pack(side="right")
        ctk.CTkLabel(
            badge,
            text=f"  {materia['creditos']} cr  ",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_primary"],
        ).pack(padx=2, pady=3)

        # ── Nombre de la materia ──────────────────────────────────────────
        ctk.CTkLabel(
            frame,
            text=materia["nombre"],
            font=FUENTE_NORMAL,
            text_color=COLORES["text_primary"],
            wraplength=720,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(5, 0))

        # ── Prerequisitos ─────────────────────────────────────────────────
        if materia["prereq"]:
            prereq_text = f"{GLYPHS['link']}  Prereq: {', '.join(materia['prereq'])}"
            prereq_color = COLORES["accent_warning"]
        else:
            prereq_text = f"{GLYPHS['check']}  Sin prerequisitos"
            prereq_color = COLORES["accent_success"]

        ctk.CTkLabel(
            frame,
            text=prereq_text,
            font=FUENTE_PEQUEÑA,
            text_color=prereq_color,
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))
