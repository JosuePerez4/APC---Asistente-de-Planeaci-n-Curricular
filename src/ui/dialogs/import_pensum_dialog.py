"""
src/ui/dialogs/import_pensum_dialog.py
======================================
Diálogo modal para importar el pénsum del portal universitario a un perfil.

Flujo en dos pasos deliberado: pegar → **Analizar** → revisar el resumen →
**Aplicar**. Aplicar directo sobre un HTML mal copiado sobrescribiría las
materias vistas del perfil sin que el usuario vea qué pasó, así que el resumen
intermedio no es opcional.

Toda la lógica vive en `pensum_import_service`; aquí solo hay presentación.
"""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from src.config.theme import (
    COLORES,
    FUENTE_H1,
    FUENTE_NORMAL,
    FUENTE_PEQUEÑA,
    GLYPHS,
)
from src.services.pensum_import_service import (
    ResultadoImportacion,
    construir_importacion,
    resumen_legible,
)

_INSTRUCCIONES = (
    "1.  Abre el pénsum en el portal de la universidad con tu sesión iniciada.\n"
    "2.  Pulsa F12 para abrir las herramientas de desarrollador.\n"
    "3.  Clic derecho sobre la tabla del pénsum  →  Copy  →  Copy outerHTML.\n"
    "4.  Pega el contenido aquí abajo y pulsa Analizar."
)


class ImportPensumDialog(ctk.CTkToplevel):
    """
    Ventana modal que convierte el HTML del portal en un conjunto de materias
    vistas y lo entrega al callback `on_aplicar` si el usuario confirma.

    Parámetros:
        master: ventana padre sobre la que se hace modal.
        nombre_perfil: nombre del perfil destino, solo para el título.
        materias_vistas_actuales: para calcular qué se desmarcaría.
        on_aplicar: callback que recibe el `set[str]` final de materias vistas.
    """

    def __init__(
        self,
        master,
        nombre_perfil: str,
        materias_vistas_actuales: set[str],
        on_aplicar: Callable[[set[str]], None],
    ) -> None:
        super().__init__(master)
        self.title(f"{GLYPHS['import']}  Importar Pénsum — {nombre_perfil}")
        self.geometry("900x680")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=COLORES["bg_deep"])

        self._materias_vistas_actuales = materias_vistas_actuales
        self._on_aplicar = on_aplicar
        self._resultado: ResultadoImportacion | None = None

        self._construir()

    # ── Construcción ─────────────────────────────────────────────────────

    def _construir(self) -> None:
        main = ctk.CTkFrame(self, fg_color=COLORES["bg_deep"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main,
            text=f"{GLYPHS['import']}  IMPORTAR PÉNSUM DESDE EL PORTAL",
            font=FUENTE_H1,
            text_color=COLORES["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        self.instrucciones_label = ctk.CTkLabel(
            main,
            text=_INSTRUCCIONES,
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_secondary"],
            justify="left",
        )
        self.instrucciones_label.pack(anchor="w", pady=(0, 12))

        # Área que alterna entre el textbox de pegado y el resumen.
        self.textbox = ctk.CTkTextbox(
            main,
            fg_color=COLORES["bg_card"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            text_color=COLORES["text_primary"],
            font=FUENTE_PEQUEÑA,
            corner_radius=10,
            wrap="none",
        )
        self.textbox.pack(fill="both", expand=True)

        # Botonera inferior
        btn_bar = ctk.CTkFrame(main, fg_color="transparent", height=60)
        btn_bar.pack(fill="x", pady=(15, 0))
        btn_bar.pack_propagate(False)

        self.accion_btn = ctk.CTkButton(
            btn_bar,
            text=f"{GLYPHS['sparkles']}  Analizar",
            command=self._analizar,
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
            font=FUENTE_NORMAL,
            height=40,
            corner_radius=8,
        )
        self.accion_btn.pack(side="left", padx=6)

        self.volver_btn = ctk.CTkButton(
            btn_bar,
            text=f"{GLYPHS['back']}  Volver a pegar",
            command=self._volver_a_pegar,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_primary"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_NORMAL,
            height=40,
            corner_radius=8,
        )
        # Solo aparece una vez hay un resumen en pantalla.

        ctk.CTkButton(
            btn_bar,
            text=f"{GLYPHS['cancel']}  Cancelar",
            command=self.destroy,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_danger"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_NORMAL,
            height=40,
            corner_radius=8,
        ).pack(side="right", padx=6)

    # ── Paso 1: analizar ─────────────────────────────────────────────────

    def _analizar(self) -> None:
        """Parsea el HTML pegado y reemplaza el textbox por el resumen."""
        html = self.textbox.get("1.0", "end").strip()
        if not html:
            self._mostrar_error("Pega primero el HTML del pénsum.")
            return

        try:
            resultado = construir_importacion(html, self._materias_vistas_actuales)
        except Exception as exc:  # noqa: BLE001 — el HTML es entrada arbitraria del usuario
            self._mostrar_error(
                f"No se pudo leer el HTML: {type(exc).__name__}: {exc}\n\n"
                "Verifica que copiaste la tabla completa del pénsum."
            )
            return

        if not resultado.materias_vistas:
            self._mostrar_error(
                "No se encontró ninguna materia aprobada en el HTML.\n\n"
                + "\n".join(resultado.avisos)
            )
            return

        self._resultado = resultado
        self._mostrar_resumen(resultado)

    def _mostrar_resumen(self, resultado: ResultadoImportacion) -> None:
        """Sustituye el contenido del textbox por el resumen y arma el paso 2."""
        self.instrucciones_label.configure(
            text="Revisa el resumen antes de aplicar. Nada se ha guardado todavía.",
            text_color=COLORES["accent_warning"]
            if (resultado.avisos or resultado.desmarcadas)
            else COLORES["text_secondary"],
        )

        self.textbox.configure(state="normal", wrap="word")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", resumen_legible(resultado))
        self.textbox.configure(state="disabled")

        self.accion_btn.configure(
            text=f"{GLYPHS['check']}  Aplicar al perfil",
            command=self._aplicar,
        )
        self.volver_btn.pack(side="left", padx=6)

    # ── Paso 2: aplicar ──────────────────────────────────────────────────

    def _aplicar(self) -> None:
        """Entrega el resultado al callback y cierra."""
        if self._resultado is None:
            return
        # El diálogo se cierra antes del callback: `on_aplicar` reconstruye la
        # vista de fondo y abre su propio mensaje de confirmación.
        materias = self._resultado.materias_vistas
        self.destroy()
        self._on_aplicar(materias)

    def _volver_a_pegar(self) -> None:
        """Vuelve al estado inicial para pegar otro HTML."""
        self._resultado = None
        self.instrucciones_label.configure(
            text=_INSTRUCCIONES,
            text_color=COLORES["text_secondary"],
        )
        self.textbox.configure(state="normal", wrap="none")
        self.textbox.delete("1.0", "end")
        self.accion_btn.configure(
            text=f"{GLYPHS['sparkles']}  Analizar",
            command=self._analizar,
        )
        self.volver_btn.pack_forget()

    # ── Utilidades ───────────────────────────────────────────────────────

    def _mostrar_error(self, mensaje: str) -> None:
        """Muestra el error en la etiqueta superior, sin perder lo pegado."""
        self.instrucciones_label.configure(
            text=mensaje,
            text_color=COLORES["accent_danger"],
        )
