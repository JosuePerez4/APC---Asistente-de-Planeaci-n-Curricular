"""
src/ui/widgets/materia_card.py
================================
Widget de solo lectura para mostrar una materia en la vista del plan de estudios.

Muestra: código con color de acento, badge de créditos, nombre completo,
prerequisitos y nota de qué materias desbloquea al aprobarla.
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
        desbloquea (list[str]): Nombres de materias que esta materia habilita al aprobarla.
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        codigo: str,
        materia: dict,
        desbloquea: list[str] | None = None,
        on_move_materia=None,
        manual_semestre: int | None = None,
        total_semestres: int = 10,
        conflictos: list[str] | None = None,
        **kwargs,
    ) -> None:
        # Determinar el color de borde según el estado de conflicto y asignación manual
        borde_color = COLORES["border_subtle"]
        if conflictos:
            borde_color = COLORES["accent_warning"]
        elif manual_semestre is not None:
            borde_color = COLORES["accent_primary"]

        super().__init__(
            parent,
            fg_color=COLORES["bg_elevated"],
            border_color=borde_color,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )
        self._construir(
            codigo,
            materia,
            desbloquea or [],
            on_move_materia,
            manual_semestre,
            total_semestres,
            conflictos or [],
        )

    def _construir(
        self,
        codigo: str,
        materia: dict,
        desbloquea: list[str],
        on_move_materia=None,
        manual_semestre: int | None = None,
        total_semestres: int = 10,
        conflictos: list[str] | None = None,
    ) -> None:
        """Construye el layout interno de la card."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=16, pady=12)

        # ── Fila superior: código, badge manual, menú y badge de créditos ──
        fila_top = ctk.CTkFrame(frame, fg_color="transparent")
        fila_top.pack(fill="x")

        # Código de la materia
        ctk.CTkLabel(
            fila_top,
            text=f"{GLYPHS['memo']}  {codigo}",
            font=FUENTE_H2,
            text_color=COLORES["accent_primary"],
            anchor="w",
        ).pack(side="left")

        # Badge indicando asignación manual
        if manual_semestre is not None:
            manual_badge = ctk.CTkFrame(
                fila_top,
                fg_color=COLORES["bg_hover"],
                border_color=COLORES["accent_primary"],
                border_width=1,
                corner_radius=6,
            )
            manual_badge.pack(side="left", padx=10)
            ctk.CTkLabel(
                manual_badge,
                text=" 📌 Manual ",
                font=FUENTE_PEQUEÑA,
                text_color=COLORES["accent_primary"],
            ).pack(padx=2, pady=1)

        # Badge de créditos (alineado a la extrema derecha)
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

        # Selector de semestre (a la izquierda de la insignia de créditos)
        if on_move_materia:
            # Opción por defecto
            default_val = "Auto (Reorganizar)"
            if manual_semestre is not None:
                default_val = f"Semestre {manual_semestre}"
                
            # Opciones: Auto, Semestre 1, ..., Semestre N+1
            options = ["Auto (Reorganizar)"] + [f"Semestre {i}" for i in range(1, total_semestres + 2)]
            
            if default_val not in options:
                options.append(default_val)

            def option_selected(val: str):
                if val.startswith("Auto"):
                    on_move_materia(codigo, None)
                else:
                    try:
                        num = int(val.split(" ")[1])
                        on_move_materia(codigo, num)
                    except (IndexError, ValueError):
                        pass

            menu = ctk.CTkOptionMenu(
                fila_top,
                values=options,
                command=option_selected,
                width=150,
                height=26,
                fg_color=COLORES["bg_hover"],
                button_color=COLORES["bg_hover"],
                button_hover_color=COLORES["accent_primary"],
                text_color=COLORES["text_secondary"],
                dropdown_fg_color=COLORES["bg_card"],
                dropdown_text_color=COLORES["text_primary"],
                dropdown_hover_color=COLORES["accent_primary"],
                font=FUENTE_PEQUEÑA,
            )
            menu.set(default_val)
            menu.pack(side="right", padx=(0, 10))

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

        # ── Advertencias de Conflictos (si existen) ───────────────────────
        if conflictos:
            for conf in conflictos:
                warn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                warn_frame.pack(anchor="w", pady=(4, 0))
                ctk.CTkLabel(
                    warn_frame,
                    text=f"⚠️  {conf}",
                    font=FUENTE_PEQUEÑA,
                    text_color=COLORES["accent_warning"],
                    anchor="w",
                ).pack(side="left")

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

        # ── Nota: materias que desbloquea ─────────────────────────────────
        if desbloquea:
            # Truncar la lista si es muy larga para no desbordar la card
            MAX_MOSTRAR = 3
            if len(desbloquea) > MAX_MOSTRAR:
                nombres = ", ".join(desbloquea[:MAX_MOSTRAR])
                desbloquea_text = (
                    f"{GLYPHS['sparkle_small']}  Desbloquea: {nombres} "
                    f"(+{len(desbloquea) - MAX_MOSTRAR} más)"
                )
            else:
                desbloquea_text = (
                    f"{GLYPHS['sparkle_small']}  Desbloquea: {', '.join(desbloquea)}"
                )

            # Separador visual tenue
            sep = ctk.CTkFrame(
                frame,
                fg_color=COLORES["border_subtle"],
                height=1,
                corner_radius=0,
            )
            sep.pack(fill="x", pady=(7, 0))

            ctk.CTkLabel(
                frame,
                text=desbloquea_text,
                font=FUENTE_PEQUEÑA,
                text_color=COLORES["accent_success"],
                wraplength=720,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(5, 0))
        else:
            # Sin materias que desbloquee directamente
            ctk.CTkLabel(
                frame,
                text=f"{GLYPHS['memo']}  No desbloquea materias nuevas directamente",
                font=FUENTE_PEQUEÑA,
                text_color=COLORES["text_muted"],
                anchor="w",
            ).pack(anchor="w", pady=(4, 0))
