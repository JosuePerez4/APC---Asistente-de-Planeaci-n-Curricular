"""
src/ui/dialogs/custom_messagebox.py
=====================================
Diálogo modal personalizado con estilo dark mode.

Reemplaza la llamada a `ctk.CTkMessageBox` (que no existe en customtkinter)
con un CTkToplevel propio que soporta 1 o 2 botones y retorna el resultado
bloqueando la ejecución hasta que el usuario responde.

Uso:
    dialogo = CustomMessageBox(
        title="Confirmar",
        message="¿Estás seguro?",
        option_1="Cancelar",
        option_2="Confirmar",
    )
    resultado = dialogo.get_result()  # Retorna "Cancelar" o "Confirmar" o None
"""
from __future__ import annotations
import customtkinter as ctk
from src.config.theme import COLORES, FUENTE_H2, FUENTE_NORMAL, FUENTE_PEQUEÑA


class CustomMessageBox(ctk.CTkToplevel):
    """
    Ventana modal con un mensaje y uno o dos botones de acción.

    Parámetros:
        title (str): Título de la ventana.
        message (str): Mensaje a mostrar al usuario.
        option_1 (str): Texto del primer botón (neutro / cancelar). Default "OK".
        option_2 (str | None): Texto del segundo botón (acción principal). Si es None,
                                solo se muestra option_1.
    """

    def __init__(
        self,
        title: str,
        message: str,
        option_1: str = "OK",
        option_2: str | None = None,
    ) -> None:
        super().__init__()
        self.title(title)
        self.geometry("440x220")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        self.configure(fg_color=COLORES["bg_card"])

        # Resultado seleccionado por el usuario
        self.result: str | None = None

        self._construir(title, message, option_1, option_2)

    # ── Construcción ─────────────────────────────────────────────────────

    def _construir(
        self,
        title: str,
        message: str,
        option_1: str,
        option_2: str | None,
    ) -> None:
        """Construye todos los widgets del diálogo."""

        # Barra de título estilizada
        title_bar = ctk.CTkFrame(
            self,
            fg_color=COLORES["bg_elevated"],
            corner_radius=0,
            height=46,
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        ctk.CTkLabel(
            title_bar,
            text=title,
            font=FUENTE_H2,
            text_color=COLORES["text_primary"],
        ).pack(expand=True)

        # Área de contenido
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=12)

        ctk.CTkLabel(
            content,
            text=message,
            font=FUENTE_NORMAL,
            text_color=COLORES["text_secondary"],
            wraplength=380,
            justify="center",
        ).pack(pady=(10, 18))

        # Botones
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack()

        if option_2:
            # Botón secundario (neutro / cancelar)
            ctk.CTkButton(
                btn_frame,
                text=option_1,
                command=lambda: self._set_result(option_1),
                fg_color=COLORES["bg_hover"],
                hover_color=COLORES["border_subtle"],
                text_color=COLORES["text_secondary"],
                font=FUENTE_NORMAL,
                width=130,
                height=38,
                corner_radius=8,
            ).pack(side="left", padx=(0, 10))

            # Botón principal (acción)
            ctk.CTkButton(
                btn_frame,
                text=option_2,
                command=lambda: self._set_result(option_2),
                fg_color=COLORES["accent_primary"],
                hover_color=COLORES["accent_glow"],
                text_color=COLORES["text_primary"],
                font=FUENTE_NORMAL,
                width=130,
                height=38,
                corner_radius=8,
            ).pack(side="left")
        else:
            # Solo un botón (informativo)
            ctk.CTkButton(
                btn_frame,
                text=option_1,
                command=lambda: self._set_result(option_1),
                fg_color=COLORES["accent_primary"],
                hover_color=COLORES["accent_glow"],
                text_color=COLORES["text_primary"],
                font=FUENTE_NORMAL,
                width=130,
                height=38,
                corner_radius=8,
            ).pack()

    # ── API pública ───────────────────────────────────────────────────────

    def _set_result(self, result: str) -> None:
        """Guarda el resultado y cierra el diálogo."""
        self.result = result
        self.destroy()

    def get_result(self) -> str | None:
        """
        Bloquea hasta que el usuario cierra el diálogo y retorna la opción elegida.
        Retorna None si el usuario cierra la ventana sin hacer clic en ningún botón.
        """
        self.wait_window()
        return self.result
