"""
src/ui/views/plan_view.py
==========================
Vista del plan de estudios personalizado y del editor de materias vistas.

Responsabilidades:
  - Mostrar la distribución semestral óptima de materias pendientes.
  - Ofrecer estadísticas globales de progreso y créditos.
  - Proporcionar un editor interactivo para marcar materias como vistas.
  - Soportar el guardado y la regeneración automática al aplicar cambios.
"""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
import customtkinter as ctk

from src.config.theme import COLORES, FUENTE_H1, FUENTE_H2, FUENTE_NORMAL, FUENTE_PEQUEÑA, GLYPHS
from src.services.perfil_service import guardar_perfiles
from src.services.planner_service import (
    generar_plan_personalizado,
    obtener_desbloqueadas_por_materia,
    obtener_materias_por_perfil,
    obtener_semestres_por_perfil,
)
from src.ui.dialogs.custom_messagebox import CustomMessageBox
from src.ui.widgets.materia_card import MateriaCard
from src.ui.widgets.materia_editor_row import MateriaEditorRow

if TYPE_CHECKING:
    from src.ui.app import PlanEstudiosApp


class PlanView:
    """
    Pantalla que muestra el plan de estudios generado por semestres,
    gráficos de progreso, y da acceso al editor de materias vistas.
    """

    def __init__(self, parent: ctk.CTkFrame, app: PlanEstudiosApp) -> None:
        self.parent = parent
        self.app = app
        self.notebook = None
        self.checkboxes_editor = {}
        self.semestres_expandidos = {}
        self.temp_materias_vistas = set()
        self._construir()

    # ── Construcción de la Vista Principal ────────────────────────────────

    def _construir(self) -> None:
        """Construye o reconstruye toda la interfaz de usuario de la vista."""
        if not self.app.perfil_actual:
            return

        # Limpiar cualquier widget anterior para la regeneración limpia
        for widget in self.parent.winfo_children():
            widget.destroy()

        self._construir_header()
        self._construir_notebook()
        self._construir_footer_stats()

    def _construir_header(self) -> None:
        """Header superior con botón volver, info del perfil y acciones."""
        header = ctk.CTkFrame(
            self.parent,
            fg_color=COLORES["bg_elevated"],
            corner_radius=16,
            height=80,
        )
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)

        # Botón volver a la pantalla de perfiles
        volver_btn = ctk.CTkButton(
            header,
            text=f"{GLYPHS['back']}  Volver a Perfiles",
            command=self.app.mostrar_perfiles,
            width=150,
            height=38,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_primary"],
            text_color=COLORES["text_primary"],
            font=FUENTE_NORMAL,
            corner_radius=8,
        )
        volver_btn.pack(side="left", padx=16, pady=20)

        # Etiqueta de información del perfil actual
        perfil = self.app.perfil_actual
        proyecto_texto = "con Proyecto de Grado" if perfil.incluir_proyecto_grado else "sin Proyecto de Grado"
        
        info_label = ctk.CTkLabel(
            header,
            text=f"{GLYPHS['user']}  {perfil.nombre}   ·   {GLYPHS['plan']}  Plan {proyecto_texto}",
            font=FUENTE_H2,
            text_color=COLORES["text_primary"],
        )
        info_label.pack(side="left", padx=20, pady=20)

        # Frame de acciones alineado a la derecha
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=16, pady=20)

        # Botón para abrir el editor modal de materias
        editar_btn = ctk.CTkButton(
            btn_frame,
            text=f"{GLYPHS['edit']}  Editar Materias",
            command=self.mostrar_editor,
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
            font=FUENTE_NORMAL,
            height=38,
            corner_radius=8,
        )
        editar_btn.pack(side="left", padx=6)

        # Botón secundario para persistir manualmente el plan actual
        guardar_btn = ctk.CTkButton(
            btn_frame,
            text=f"{GLYPHS['save']}  Guardar Plan",
            command=self.guardar_plan,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_primary"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_NORMAL,
            height=38,
            corner_radius=8,
        )
        guardar_btn.pack(side="left", padx=6)

    def _construir_notebook(self) -> None:
        """Pestañas por cada semestre con la lista de materias sugeridas."""
        notebook_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        notebook_frame.pack(fill="both", expand=True)

        self.notebook = ctk.CTkTabview(
            notebook_frame,
            segmented_button_fg_color=COLORES["bg_card"],
            segmented_button_selected_color=COLORES["accent_primary"],
            segmented_button_selected_hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
        )
        self.notebook.pack(fill="both", expand=True)

        perfil = self.app.perfil_actual
        plan = generar_plan_personalizado(perfil)
        materias_perfil = obtener_materias_por_perfil(perfil)

        if not plan:
            self.notebook.add(f"{GLYPHS['book']} Sin Pendientes")
            tab = self.notebook.tab(f"{GLYPHS['book']} Sin Pendientes")
            tab.configure(fg_color=COLORES["bg_deep"])
            
            ctk.CTkLabel(
                tab,
                text=f"{GLYPHS['sparkles']}  ¡Felicidades! Has completado todas las materias de tu plan de estudios.",
                font=FUENTE_H2,
                text_color=COLORES["accent_success"],
            ).pack(expand=True)
            return

        for semestre_num, materias_sem in plan:
            tab_name = f"{GLYPHS['book']} Semestre {semestre_num}"
            self.notebook.add(tab_name)
            
            tab = self.notebook.tab(tab_name)
            tab.configure(fg_color=COLORES["bg_deep"])

            # Calcular créditos totales sugeridos para este semestre
            creditos_sem = sum(
                materias_perfil[cod]["creditos"]
                for cod in materias_sem
                if cod in materias_perfil
            )
            
            title_frame = ctk.CTkFrame(tab, fg_color="transparent")
            title_frame.pack(fill="x", pady=(8, 12))

            ctk.CTkLabel(
                title_frame,
                text=f"{GLYPHS['book']} SEMESTRE {semestre_num}  ·  {creditos_sem} CRÉDITOS SUGERIDOS",
                font=FUENTE_H2,
                text_color=COLORES["text_primary"],
            ).pack(side="left", padx=6)

            # Contenedor scrollable
            scroll = ctk.CTkScrollableFrame(
                tab,
                fg_color=COLORES["bg_deep"],
                border_color=COLORES["border_subtle"],
                border_width=1,
                corner_radius=10,
            )
            scroll.pack(fill="both", expand=True, padx=4, pady=4)

            # Instanciar cards para cada materia
            for cod in materias_sem:
                if cod in materias_perfil:
                    desbloquea = obtener_desbloqueadas_por_materia(cod, perfil)
                    card = MateriaCard(scroll, cod, materias_perfil[cod], desbloquea=desbloquea)
                    card.pack(fill="x", pady=6, padx=6)

    def _construir_footer_stats(self) -> None:
        """Barra de estado inferior que muestra el progreso global del estudiante."""
        stats_frame = ctk.CTkFrame(
            self.parent,
            fg_color=COLORES["bg_elevated"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            corner_radius=12,
            height=70,
        )
        stats_frame.pack(fill="x", pady=(15, 0))
        stats_frame.pack_propagate(False)

        perfil = self.app.perfil_actual
        materias_perfil = obtener_materias_por_perfil(perfil)
        
        total_mats = len(materias_perfil)
        vistas_mats = len(perfil.materias_vistas)
        faltantes_mats = total_mats - vistas_mats

        total_cred = sum(m["creditos"] for m in materias_perfil.values())
        vistas_cred = sum(
            materias_perfil[cod]["creditos"]
            for cod in perfil.materias_vistas
            if cod in materias_perfil
        )

        porcentaje = (vistas_mats / total_mats * 100) if total_mats > 0 else 0.0
        proyecto_texto = "con Proyecto de Grado" if perfil.incluir_proyecto_grado else "sin Proyecto de Grado"

        stats_text = (
            f"{GLYPHS['plan']}  PROGRESO {proyecto_texto.upper()}: {vistas_mats}/{total_mats} materias ({porcentaje:.1f}%)   ·   "
            f"{GLYPHS['target']}  {vistas_cred}/{total_cred} créditos aprobados   ·   "
            f"{GLYPHS['calendar']}  Faltan: {faltantes_mats} materias"
        )

        inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            inner,
            text=stats_text,
            font=FUENTE_H2,
            text_color=COLORES["text_primary"],
        ).pack(side="left")

        # Barra de progreso visual
        prog_bar = ctk.CTkProgressBar(
            inner,
            width=220,
            height=10,
            fg_color=COLORES["bg_hover"],
            progress_color=COLORES["accent_success"],
        )
        prog_bar.pack(side="right", padx=(10, 0))
        prog_bar.set(porcentaje / 100.0)

    # ── Guardado Manual del Plan ──────────────────────────────────────────

    def guardar_plan(self) -> None:
        """Persiste el plan actual de estudios actualizando la fecha."""
        self.app.perfil_actual.fecha_actualizacion = datetime.now().isoformat()
        try:
            guardar_perfiles(self.app.perfiles)
            CustomMessageBox(
                title=f"{GLYPHS['save']}  Guardado Exitoso",
                message="Tu plan se ha guardado correctamente en perfiles_estudios.json.",
            ).get_result()
        except RuntimeError as exc:
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error al Guardar",
                message=f"No se pudieron guardar los perfiles:\n{exc}",
            ).get_result()

    # ── Editor de Materias Vistas (Modal) ─────────────────────────────────

    def mostrar_editor(self) -> None:
        """Abre la ventana modal interactiva del editor de materias."""
        editor = ctk.CTkToplevel(self.parent.winfo_toplevel())
        editor.title(f"{GLYPHS['edit']}  Editor de Materias — {self.app.perfil_actual.nombre}")
        editor.geometry("1100x750")
        editor.transient(self.parent.winfo_toplevel())
        editor.grab_set()

        # Copia temporal de materias vistas para no alterar el perfil en vivo antes de Aplicar
        self.temp_materias_vistas = set(self.app.perfil_actual.materias_vistas)
        self.checkboxes_editor = {}
        self.semestres_expandidos = {}

        # Frame contenedor
        main_frame = ctk.CTkFrame(editor, fg_color=COLORES["bg_deep"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header del editor
        proyecto_texto = "con Proyecto de Grado" if self.app.perfil_actual.incluir_proyecto_grado else "sin Proyecto de Grado"
        ctk.CTkLabel(
            main_frame,
            text=f"{GLYPHS['edit']}  EDITANDO MATERIAS VISTAS — {self.app.perfil_actual.nombre} ({proyecto_texto})",
            font=FUENTE_H1,
            text_color=COLORES["text_primary"],
        ).pack(pady=(0, 15), anchor="w")

        # Scrollable de semestres
        scroll = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=COLORES["bg_card"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            corner_radius=12,
        )
        scroll.pack(fill="both", expand=True)

        semestres_perfil = obtener_semestres_por_perfil(self.app.perfil_actual)

        for sem_num, materias_sem in semestres_perfil.items():
            self._construir_semestre_colapsable(scroll, sem_num, materias_sem)

        # Botones de acción inferiores
        btn_bar = ctk.CTkFrame(main_frame, fg_color="transparent", height=60)
        btn_bar.pack(fill="x", pady=(15, 0))
        btn_bar.pack_propagate(False)

        aplicar_btn = ctk.CTkButton(
            btn_bar,
            text=f"{GLYPHS['check']}  Aplicar Cambios y Regenerar",
            command=lambda: self.aplicar_cambios_editor(editor),
            fg_color=COLORES["accent_primary"],
            hover_color=COLORES["accent_glow"],
            text_color=COLORES["text_primary"],
            font=FUENTE_NORMAL,
            height=40,
            corner_radius=8,
        )
        aplicar_btn.pack(side="left", padx=6)

        cancelar_btn = ctk.CTkButton(
            btn_bar,
            text=f"{GLYPHS['cancel']}  Cancelar",
            command=editor.destroy,
            fg_color=COLORES["bg_hover"],
            hover_color=COLORES["accent_danger"],
            text_color=COLORES["text_secondary"],
            font=FUENTE_NORMAL,
            height=40,
            corner_radius=8,
        )
        cancelar_btn.pack(side="right", padx=6)

    def _construir_semestre_colapsable(
        self, parent: ctk.CTkBaseClass, sem_num: int, materias_sem: dict[str, dict]
    ) -> None:
        """Construye un módulo colapsable para un semestre en el editor."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORES["bg_deep"],
            border_color=COLORES["border_subtle"],
            border_width=1,
            corner_radius=10,
        )
        card.pack(fill="x", pady=8, padx=6)

        # Header del colapsable
        header = ctk.CTkFrame(card, fg_color=COLORES["bg_elevated"], corner_radius=10)
        header.pack(fill="x", padx=1, pady=1)

        # Botón que expande o colapsa el frame
        toggle_btn = ctk.CTkButton(
            header,
            text=f"{GLYPHS['book']}  Semestre {sem_num}",
            font=FUENTE_H2,
            fg_color="transparent",
            hover_color=COLORES["bg_hover"],
            text_color=COLORES["text_primary"],
            anchor="w",
            command=lambda: self.toggle_semestre(sem_num),
        )
        toggle_btn.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        # Contador de materias vistas en este semestre
        vistas_sem = sum(1 for cod in materias_sem if cod in self.temp_materias_vistas)
        count_label = ctk.CTkLabel(
            header,
            text=f"({vistas_sem}/{len(materias_sem)} vistas)  ",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["text_secondary"],
        )
        count_label.pack(side="right", padx=8)

        # Contenedor de materias internas
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=(8, 12))

        self.semestres_expandidos[sem_num] = {
            "content_frame": content,
            "expanded": True,
            "count_label": count_label,
            "materias_sem": materias_sem,
        }

        # Instanciar fila interactiva para cada materia
        for cod, mat in materias_sem.items():
            is_checked = cod in self.temp_materias_vistas
            row = MateriaEditorRow(
                content,
                codigo=cod,
                materia=mat,
                is_checked=is_checked,
                on_toggle=self.toggle_materia_editor,
            )
            row.pack(fill="x", pady=4)

    def toggle_semestre(self, sem_num: int) -> None:
        """Muestra o esconde el panel de materias de un semestre en el editor."""
        estado = self.semestres_expandidos[sem_num]
        if estado["expanded"]:
            estado["content_frame"].pack_forget()
            estado["expanded"] = False
        else:
            estado["content_frame"].pack(fill="x", padx=12, pady=(8, 12))
            estado["expanded"] = True

    def toggle_materia_editor(self, codigo: str, var: ctk.BooleanVar) -> None:
        """Callback del checkbox para actualizar el set temporal de aprobadas."""
        if var.get():
            self.temp_materias_vistas.add(codigo)
        else:
            self.temp_materias_vistas.discard(codigo)

        # Actualizar dinámicamente los contadores de vista rápida
        for sem_num, estado in self.semestres_expandidos.items():
            materias_sem = estado["materias_sem"]
            if codigo in materias_sem:
                vistas_sem = sum(1 for cod in materias_sem if cod in self.temp_materias_vistas)
                estado["count_label"].configure(text=f"({vistas_sem}/{len(materias_sem)} vistas)  ")

    def aplicar_cambios_editor(self, editor: ctk.CTkToplevel) -> None:
        """Aplica los cambios del editor al perfil real, guarda y regenera."""
        self.app.perfil_actual.materias_vistas = self.temp_materias_vistas
        self.app.perfil_actual.fecha_actualizacion = datetime.now().isoformat()
        
        try:
            guardar_perfiles(self.app.perfiles)
            editor.destroy()
            self._construir()
            CustomMessageBox(
                title=f"{GLYPHS['check']}  Éxito",
                message="Plan regenerado con los nuevos cambios.",
            ).get_result()
        except RuntimeError as exc:
            CustomMessageBox(
                title=f"{GLYPHS['cancel']}  Error al Guardar",
                message=f"No se pudieron aplicar los cambios:\n{exc}",
            ).get_result()
