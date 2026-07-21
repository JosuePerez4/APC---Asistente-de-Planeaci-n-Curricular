"""
src/ui/app.py
============
Orquestador principal de la interfaz gráfica y navegación de APC.

Responsabilidades:
  - Inicializar la ventana principal de customtkinter.
  - Administrar el estado de perfiles cargados y perfil_actual.
  - Proveer funciones de enrutamiento limpio: mostrar_perfiles() / mostrar_plan().
"""

from __future__ import annotations
import customtkinter as ctk

from src.config.theme import COLORES
from src.services.perfil_service import cargar_perfiles
from src.ui.views.perfil_view import PerfilView
from src.ui.views.plan_view import PlanView


class PlanEstudiosApp:
    """
    Controlador principal de la GUI de la aplicación.
    Maneja la navegación entre la selección de perfiles y el plan de estudios.
    """

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Asistente de Planeación Curricular — APC")
        self.root.geometry("1400x850")

        # Configurar apariencia del root frame
        self.root.configure(fg_color=COLORES["bg_deep"])

        # Estado global
        self.perfiles = cargar_perfiles()
        self.perfil_actual = None

        # Contenedor principal de vistas
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=24, pady=24)

        # Iniciar en la pantalla de perfiles
        self.mostrar_perfiles()

    def limpiar_pantalla(self) -> None:
        """Elimina todos los widgets contenidos en el frame principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def mostrar_perfiles(self) -> None:
        """Navega a la vista de selección de perfiles."""
        self.limpiar_pantalla()
        # Recargar perfiles para asegurar consistencia
        self.perfiles = cargar_perfiles()
        self.view = PerfilView(self.main_frame, self)

    def mostrar_plan(self) -> None:
        """Navega a la vista de visualización y edición del plan de estudios."""
        self.limpiar_pantalla()
        self.view = PlanView(self.main_frame, self)
