import itertools
import json
import os
from datetime import datetime
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

COLORES = {
    "color1": "#8d7966",
    "color2": "#a8a39d", 
    "color3": "#d8c8b8",
    "color4": "#e2ddd9",
    "color5": "#f8f1e9",
    "texto_oscuro": "#5a4a3a",
    "texto_claro": "#7a6a5a",
}

FUENTE_TITULOS = ("Segoe UI Emoji", 16, "bold")
FUENTE_NORMAL = ("Segoe UI Emoji", 12)
FUENTE_PEQUEÑA = ("Segoe UI Emoji", 10)

semestres = {
    1: {
        "1155101": {"nombre": "CALCULO DIFERENCIAL", "creditos": 4, "prereq": [], "reqCred": 0},
        "1155102": {"nombre": "MATEMATICAS DISCRETAS", "creditos": 3, "prereq": [], "reqCred": 0},
        "1155104": {"nombre": "FUNDAMENTOS DE PROGRAMACION", "creditos": 3, "prereq": [], "reqCred": 0},
        "1155105": {"nombre": "INTRO A INGENIERIA DE SISTEMAS", "creditos": 3, "prereq": [], "reqCred": 0},
        "1155106": {"nombre": "COMUNICACION I", "creditos": 2, "prereq": [], "reqCred": 0},
        "1155108": {"nombre": "INTROD. A LA VIDA UNIVERSITARIA", "creditos": 1, "prereq": [], "reqCred": 0},
    },
    2: {
        "1155201": {"nombre": "CALCULO INTEGRAL", "creditos": 4, "prereq": ["1155101"], "reqCred": 0},
        "1155202": {"nombre": "ALGEBRA LINEAL", "creditos": 3, "prereq": ["1155101"], "reqCred": 0},
        "1155203": {"nombre": "FISICA MECANICA", "creditos": 4, "prereq": ["1155101"], "reqCred": 0},
        "1155204": {"nombre": "PROGR ORIENTADA A OBJETOS I", "creditos": 3, "prereq": ["1155104"], "reqCred": 0},
        "1155206": {"nombre": "COMUNICACION II", "creditos": 2, "prereq": ["1155106"], "reqCred": 0},
        "1155209": {"nombre": "SEMINARIO INTEGRADOR I", "creditos": 1, "prereq": ["1155104"], "reqCred": 0},
    },
    3: {
        "1155301": {"nombre": "CALCULO VECTORIAL", "creditos": 4, "prereq": ["1155201"], "reqCred": 0},
        "1155303": {"nombre": "FISICA ELECTROMAGNETICA", "creditos": 4, "prereq": ["1155203"], "reqCred": 0},
        "1155304": {"nombre": "ESTRUCTURA DE DATOS", "creditos": 3, "prereq": ["1155204"], "reqCred": 0},
        "1155305": {"nombre": "PROGR ORIENTADA A OBJETOS II", "creditos": 3, "prereq": ["1155204"], "reqCred": 0},
        "1155306": {"nombre": "SEMINARIO DE INVESTIGACION I", "creditos": 2, "prereq": ["1155209"], "reqCred": 23},
    },
    4: {
        "1155401": {"nombre": "ECUACIONES DIFERENCIALES", "creditos": 4, "prereq": ["1155301"], "reqCred": 0},
        "1155402": {"nombre": "PROBABILIDAD Y ESTADISTICA", "creditos": 3, "prereq": ["1155102"], "reqCred": 0},
        "1155403": {"nombre": "ONDAS Y PARTICULAS", "creditos": 3, "prereq": ["1155303"], "reqCred": 0},
        "1155404": {"nombre": "ANALISIS DE ALGORITMOS", "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
        "1155405": {"nombre": "TEORIA DE LA COMPUTACION", "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
    },
    5: {
        "1155501": {"nombre": "ANALISIS NUMERICO", "creditos": 3, "prereq": ["1155401"], "reqCred": 0},
        "1155502": {"nombre": "INVESTIGACIÓN DE OPERACIONES", "creditos": 3, "prereq": ["1155402"], "reqCred": 0},
        "1155503": {"nombre": "ELECTRONICA", "creditos": 3, "prereq": ["1155403"], "reqCred": 0},
        "1155504": {"nombre": "ARQUITECTURA DE COMPUTADORES", "creditos": 3, "prereq": ["1155304"], "reqCred": 0},
        "1155506": {"nombre": "SEMINARIO DE INVESTIGACIÓN II", "creditos": 2, "prereq": ["1155306"], "reqCred": 0},
        "SOCIOHUMANISTICA_I": {"nombre": "ELECTIVA SOCIOHUMANISTICA I", "creditos": 2, "prereq": [], "reqCred": 0},
    },
    6: {
        "1155604": {"nombre": "SISTEMAS OPERATIVOS", "creditos": 3, "prereq": ["1155504"], "reqCred": 0},
        "1155605": {"nombre": "BASES DE DATOS", "creditos": 3, "prereq": ["1155304", "1155305"], "reqCred": 0},
        "1155606": {"nombre": "PROGRAMACION WEB", "creditos": 3, "prereq": ["1155305", "1155304"], "reqCred": 0},
        "1155607": {"nombre": "CONSTITUCION Y CIVISMO", "creditos": 2, "prereq": [], "reqCred": 20},
        "1155608": {"nombre": "PLANEACION ESTRATEGICA DE SI", "creditos": 3, "prereq": [], "reqCred": 48},
        "1155609": {"nombre": "SEMINARIO INTEGRADOR II", "creditos": 2, "prereq": ["1155209", "1155304"], "reqCred": 75},
        "ELECTIVA_PROFESIONAL_I": {"nombre": "ELECTIVA PROFESIONAL I", "creditos": 3, "prereq": [], "reqCred": 0},
    },
    7: {
        "1155704": {"nombre": "TEORÍA GENERAL DE LAS COMUNICACIONES", "creditos": 3, "prereq": ["1155604"], "reqCred": 0},
        "1155705": {"nombre": "ANÁLISIS Y DISEÑO DE SISTEMAS", "creditos": 4, "prereq": ["1155605"], "reqCred": 0},
        "1155706": {"nombre": "SEMINARIO DE INVESTIGACION III", "creditos": 2, "prereq": ["1155506"], "reqCred": 0},
        "1155707": {"nombre": "ETICA PROFESIONAL", "creditos": 2, "prereq": [], "reqCred": 90},
        "1155708": {"nombre": "ADMINISTACION DE PROYECTOS INFORMÁTICOS", "creditos": 3, "prereq": ["1155608"], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_II": {"nombre": "ELECTIVA PROFESIONAL II", "creditos": 3, "prereq": [], "reqCred": 0},
    },
    8: {
        "1155804": {"nombre": "REDES DE COMPUTADORES", "creditos": 3, "prereq": ["1155704"], "reqCred": 0},
        "1155805": {"nombre": "INGENIERÍA DE SOFTWARE", "creditos": 4, "prereq": ["1155705"], "reqCred": 0},
        "1155808": {"nombre": "FORMULACION Y EVALUACION DE PROYECTOS DE SISTEMAS", "creditos": 3, "prereq": ["1155708"], "reqCred": 0},
        "1155809": {"nombre": "SEMINARIO INTEGRADOR III", "creditos": 2, "prereq": ["1155705", "1155606", "1155609"], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_III": {"nombre": "ELECTIVA PROFESIONAL III", "creditos": 3, "prereq": [], "reqCred": 0},
        "SOCIOHUMANISTICA_II": {"nombre": "ELECTIVA SOCIOHUMANISTICA II", "creditos": 2, "prereq": [], "reqCred": 0},
    },
    9: {
        "1155908": {"nombre": "GESTION DE TIC", "creditos": 2, "prereq": ["1155808"], "reqCred": 0},
        "1155909": {"nombre": "PRACTICA EN SISTEMAS", "creditos": 6, "prereq": [], "reqCred": 130},
        "1155905": {"nombre": "ARQUITECTURA DE SOFTWARE", "creditos": 3, "prereq": ["1155805"], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_IV": {"nombre": "ELECTIVA PROFESIONAL IV", "creditos": 3, "prereq": [], "reqCred": 0},
    },
    10: {
        "1156001": {"nombre": "PROYECTO DE GRADO", "creditos": 8, "prereq": [], "reqCred": 100},
        "ELECTIVA_PROFESIONAL_V": {"nombre": "ELECTIVA PROFESIONAL V", "creditos": 3, "prereq": [], "reqCred": 0},
        "ELECTIVA_PROFESIONAL_VI": {"nombre": "ELECTIVA PROFESIONAL VI", "creditos": 3, "prereq": [], "reqCred": 0},
        "SOCIOHUMANISTICA_III": {"nombre": "ELECTIVA SOCIOHUMANISTICA III", "creditos": 2, "prereq": [], "reqCred": 0},
    }
}

materias = {}
for semestre, materias_sem in semestres.items():
    materias.update(materias_sem)

PROFILES_FILE = "perfiles_estudios.json"

class PerfilEstudiante:
    def __init__(self, nombre, materias_vistas=None, fecha_creacion=None, incluir_proyecto_grado=True):
        self.nombre = nombre
        self.materias_vistas = set(materias_vistas) if materias_vistas else set()
        self.fecha_creacion = fecha_creacion or datetime.now().isoformat()
        self.fecha_actualizacion = datetime.now().isoformat()
        self.incluir_proyecto_grado = incluir_proyecto_grado
    
    def to_dict(self):
        return {
            'nombre': self.nombre,
            'materias_vistas': list(self.materias_vistas),
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
            'incluir_proyecto_grado': self.incluir_proyecto_grado
        }
    
    @classmethod
    def from_dict(cls, data):
        perfil = cls(data['nombre'], data['materias_vistas'], data['fecha_creacion'])
        perfil.fecha_actualizacion = data.get('fecha_actualizacion', perfil.fecha_creacion)
        perfil.incluir_proyecto_grado = data.get('incluir_proyecto_grado', True)
        return perfil

def cargar_perfiles():
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                return {nombre: PerfilEstudiante.from_dict(perfil_data) 
                       for nombre, perfil_data in datos.items()}
        except Exception as e:
            print(f"Error cargando perfiles: {e}")
    return {}

def guardar_perfiles(perfiles):
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            datos = {nombre: perfil.to_dict() for nombre, perfil in perfiles.items()}
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        ctk.CTkMessageBox(title="Error", message=f"No se pudieron guardar los perfiles: {e}", icon="cancel")

def obtener_materias_por_perfil(perfil):
    if perfil.incluir_proyecto_grado:
        return materias.copy()
    else:
        materias_filtradas = materias.copy()
        if "1156001" in materias_filtradas:
            del materias_filtradas["1156001"]
        return materias_filtradas

def obtener_semestres_por_perfil(perfil):
    if perfil.incluir_proyecto_grado:
        return semestres.copy()
    else:
        semestres_filtrados = semestres.copy()
        if 10 in semestres_filtrados:
            semestre_10_filtrado = semestres_filtrados[10].copy()
            if "1156001" in semestre_10_filtrado:
                del semestre_10_filtrado["1156001"]
            semestres_filtrados[10] = semestre_10_filtrado
        return semestres_filtrados

def materias_habilitadas(aprobadas, creditos_actuales, materias_vistas, perfil):
    materias_perfil = obtener_materias_por_perfil(perfil)
    disponibles = []
    for codigo, data in materias_perfil.items():
        if codigo in aprobadas or codigo in materias_vistas:
            continue
        if creditos_actuales < data["reqCred"]:
            continue
        prerequisitos_cumplidos = all(pr in aprobadas or pr in materias_vistas for pr in data["prereq"])
        if prerequisitos_cumplidos:
            disponibles.append(codigo)
    return disponibles

def mejor_combinacion(disponibles, perfil):
    materias_perfil = obtener_materias_por_perfil(perfil)
    best = []
    best_creditos = 0

    for r in range(1, len(disponibles) + 1):
        for combo in itertools.combinations(disponibles, r):
            total = sum(materias_perfil[c]["creditos"] for c in combo)
            if total <= 20 and total > best_creditos:
                best = combo
                best_creditos = total

    return list(best)

def generar_plan_personalizado(perfil):
    materias_vistas = perfil.materias_vistas
    materias_perfil = obtener_materias_por_perfil(perfil)
    semestres_perfil = obtener_semestres_por_perfil(perfil)
    
    if len(materias_vistas) == 0:
        plan_original = []
        for semestre_num, materias_sem in semestres_perfil.items():
            plan_original.append((semestre_num, list(materias_sem.keys())))
        return plan_original
    
    aprobadas = []
    creditos = sum(materias_perfil[cod]['creditos'] for cod in materias_vistas)
    semestre = 1
    plan = []
    
    materias_faltantes = set(materias_perfil.keys()) - set(materias_vistas)

    while len(aprobadas) < len(materias_faltantes):
        dispo = materias_habilitadas(aprobadas, creditos, materias_vistas, perfil)

        if not dispo:
            break

        combo = mejor_combinacion(dispo, perfil)
        if not combo:
            break

        plan.append((semestre, combo))

        for c in combo:
            aprobadas.append(c)
            creditos += materias_perfil[c]["creditos"]

        semestre += 1

    return plan

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message, option_1="OK", option_2=None):
        super().__init__()
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
        self.result = None
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORES["color5"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame, 
            text=message, 
            font=FUENTE_NORMAL,
            text_color=COLORES["texto_oscuro"],
            wraplength=350
        )
        message_label.pack(pady=20)
        
        # Frame para botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        if option_2:
            btn1 = ctk.CTkButton(
                button_frame, 
                text=option_1, 
                command=lambda: self.set_result(option_1),
                fg_color=COLORES["color2"],
                hover_color=COLORES["color1"],
                font=FUENTE_NORMAL
            )
            btn1.pack(side="left", padx=10)
            
            btn2 = ctk.CTkButton(
                button_frame, 
                text=option_2, 
                command=lambda: self.set_result(option_2),
                fg_color=COLORES["color1"],
                hover_color=COLORES["texto_oscuro"],
                font=FUENTE_NORMAL
            )
            btn2.pack(side="left", padx=10)
        else:
            btn = ctk.CTkButton(
                button_frame, 
                text=option_1, 
                command=lambda: self.set_result(option_1),
                fg_color=COLORES["color1"],
                hover_color=COLORES["texto_oscuro"],
                font=FUENTE_NORMAL
            )
            btn.pack(padx=10)
    
    def set_result(self, result):
        self.result = result
        self.destroy()
    
    def get_result(self):
        self.wait_window()
        return self.result

class PlanEstudiosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador de Estudios - Sistema Multiperfil")
        self.root.geometry("1400x850")
        
        # Configurar el fondo principal
        self.root.configure(fg_color=COLORES["color5"])
        
        self.perfiles = cargar_perfiles()
        self.perfil_actual = None
        self.checkboxes = {}
        self.semestres_expandidos = {}
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLORES["color5"])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.mostrar_pantalla_seleccion_perfiles()
    
    def mostrar_pantalla_seleccion_perfiles(self):
        self.limpiar_pantalla()
        
        # Título principal
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🎓 PLANIFICADOR DE ESTUDIOS - SELECCIONA TU PERFIL",
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        title_label.pack(pady=(20, 40))
        
        # Frame para perfiles
        profiles_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            height=500,
            fg_color=COLORES["color4"],
            border_width=2,
            border_color=COLORES["color3"]
        )
        profiles_frame.pack(fill="both", expand=True, padx=20)
        
        if self.perfiles:
            # Título de perfiles existentes
            existent_label = ctk.CTkLabel(
                profiles_frame,
                text="📂 Perfiles Existentes:",
                font=FUENTE_TITULOS,
                text_color=COLORES["texto_oscuro"]
            )
            existent_label.pack(pady=(0, 20))
            
            # Grid para perfiles
            grid_frame = ctk.CTkFrame(profiles_frame, fg_color="transparent")
            grid_frame.pack(fill="x", pady=10)
            
            row, col = 0, 0
            for i, nombre_perfil in enumerate(self.perfiles.keys()):
                perfil = self.perfiles[nombre_perfil]
                fecha = datetime.fromisoformat(perfil.fecha_actualizacion).strftime("%d/%m/%Y")
                materias_vistas = len(perfil.materias_vistas)
                proyecto_grado = "Si" if perfil.incluir_proyecto_grado else "No"
                
                # Card para cada perfil
                perfil_card = ctk.CTkFrame(
                    grid_frame,
                    border_width=2,
                    border_color=COLORES["color1"],
                    corner_radius=15,
                    fg_color=COLORES["color5"]
                )
                perfil_card.grid(
                    row=row, column=col, 
                    padx=10, pady=10, 
                    sticky="nsew"
                )
                
                # Configurar grid para expansión
                grid_frame.grid_columnconfigure(col, weight=1)
                
                # Contenido de la card
                content_frame = ctk.CTkFrame(perfil_card, fg_color="transparent")
                content_frame.pack(fill="both", expand=True, padx=15, pady=15)
                
                # Nombre del perfil
                name_label = ctk.CTkLabel(
                    content_frame,
                    text=f"👤 {nombre_perfil}",
                    font=FUENTE_TITULOS,
                    text_color=COLORES["texto_oscuro"]
                )
                name_label.pack(anchor="w", pady=(0, 10))
                
                # Información del perfil
                info_text = f"📅 Actualizado: {fecha}\n📚 {materias_vistas} materias vistas\n🎓 Proyecto: {proyecto_grado}"
                info_label = ctk.CTkLabel(
                    content_frame,
                    text=info_text,
                    font=FUENTE_NORMAL,
                    justify="left",
                    text_color=COLORES["texto_claro"]
                )
                info_label.pack(anchor="w", pady=(0, 15))
                
                # Botones de acción
                btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                btn_frame.pack(fill="x")
                
                seleccionar_btn = ctk.CTkButton(
                    btn_frame,
                    text="Seleccionar",
                    command=lambda np=nombre_perfil: self.seleccionar_perfil(np),
                    fg_color=COLORES["color1"],
                    hover_color=COLORES["texto_oscuro"],
                    font=FUENTE_NORMAL,
                    text_color=COLORES["color5"]
                )
                seleccionar_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
                
                eliminar_btn = ctk.CTkButton(
                    btn_frame,
                    text="🗑️",
                    command=lambda np=nombre_perfil: self.eliminar_perfil(np),
                    width=50,
                    fg_color=COLORES["color2"],
                    hover_color=COLORES["color1"],
                    font=FUENTE_NORMAL
                )
                eliminar_btn.pack(side="right")
                
                # Actualizar índices de grid
                col += 1
                if col >= 2:  # 2 columnas
                    col = 0
                    row += 1
        
        # Sección para nuevo perfil
        nuevo_label = ctk.CTkLabel(
            profiles_frame,
            text="➕ Crear Nuevo Perfil:",
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        nuevo_label.pack(pady=(40, 10))
        
        agregar_btn = ctk.CTkButton(
            profiles_frame,
            text="✨ CREAR NUEVO PERFIL",
            command=self.crear_nuevo_perfil_desde_seleccion,
            height=50,
            font=FUENTE_TITULOS,
            fg_color=COLORES["color1"],
            hover_color=COLORES["texto_oscuro"],
            text_color=COLORES["color5"]
        )
        agregar_btn.pack(pady=20, fill="x", padx=50)
    
    def crear_nuevo_perfil_desde_seleccion(self):
        dialog = ctk.CTkInputDialog(
            text="👤 Ingresa el nombre del nuevo perfil:",
            title="➕ Nuevo Perfil"
        )
        nombre = dialog.get_input()
        
        if nombre:
            if nombre in self.perfiles:
                ctk.CTkMessageBox(
                    title="Error",
                    message=f"Ya existe un perfil con el nombre '{nombre}'",
                    icon="cancel"
                )
                return
            
            # Diálogo personalizado para proyecto de grado
            msg = CustomMessageBox(
                title="🎓 Proyecto de Grado",
                message="¿Incluir Proyecto de Grado en tu plan de estudios?\n\nSi: Tu plan incluirá Proyecto de Grado\nNo: Tu plan no incluirá Proyecto de Grado",
                option_1="No",
                option_2="Si"
            )
            resultado = msg.get_result()
            
            incluir_proyecto = (resultado == "Si")
            
            self.perfil_actual = PerfilEstudiante(nombre, incluir_proyecto_grado=incluir_proyecto)
            self.perfiles[nombre] = self.perfil_actual
            guardar_perfiles(self.perfiles)
            
            self.mostrar_plan_estudios_automatico()
    
    def eliminar_perfil(self, nombre_perfil):
        confirm = CustomMessageBox(
            title="⚠️ Confirmar Eliminación",
            message=f"¿Estás seguro de que quieres eliminar el perfil '{nombre_perfil}'?\nEsta acción no se puede deshacer.",
            option_1="Cancelar",
            option_2="Eliminar"
        )
        
        if confirm.get_result() == "Eliminar":
            del self.perfiles[nombre_perfil]
            guardar_perfiles(self.perfiles)
            
            if self.perfil_actual and self.perfil_actual.nombre == nombre_perfil:
                self.perfil_actual = None
            
            self.mostrar_pantalla_seleccion_perfiles()
            
            ctk.CTkMessageBox(
                title="Éxito",
                message=f"Perfil '{nombre_perfil}' eliminado correctamente",
                icon="check"
            )
    
    def seleccionar_perfil(self, nombre_perfil):
        self.perfil_actual = self.perfiles[nombre_perfil]
        self.mostrar_plan_estudios_automatico()
    
    def mostrar_plan_estudios_automatico(self):
        self.limpiar_pantalla()
        
        # Header superior
        header_frame = ctk.CTkFrame(
            self.main_frame, 
            height=80,
            fg_color=COLORES["color3"],
            border_width=2,
            border_color=COLORES["color1"]
        )
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Botón volver
        volver_btn = ctk.CTkButton(
            header_frame,
            text="🔙 Volver a Perfiles",
            command=self.mostrar_pantalla_seleccion_perfiles,
            width=150,
            fg_color=COLORES["color2"],
            hover_color=COLORES["color1"],
            font=FUENTE_NORMAL,
            text_color=COLORES["color5"]
        )
        volver_btn.pack(side="left", padx=20, pady=20)
        
        # Información del perfil
        proyecto_texto = "con Proyecto de Grado" if self.perfil_actual.incluir_proyecto_grado else "sin Proyecto de Grado"
        perfil_info = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.perfil_actual.nombre} | 📋 Plan Personalizado {proyecto_texto}",
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        perfil_info.pack(side="left", padx=20, pady=20)
        
        # Botones de acción
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right", padx=20, pady=20)
        
        editar_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Editar Materias",
            command=self.mostrar_editor_materias,
            fg_color=COLORES["color1"],
            hover_color=COLORES["texto_oscuro"],
            font=FUENTE_NORMAL,
            text_color=COLORES["color5"]
        )
        editar_btn.pack(side="left", padx=5)
        
        guardar_btn = ctk.CTkButton(
            action_frame,
            text="💾 Guardar Plan",
            command=self.guardar_y_regenerar,
            fg_color=COLORES["color1"],
            hover_color=COLORES["texto_oscuro"],
            font=FUENTE_NORMAL,
            text_color=COLORES["color5"]
        )
        guardar_btn.pack(side="left", padx=5)
        
        # Notebook para semestres
        notebook_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORES["color4"]
        )
        notebook_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.notebook = ctk.CTkTabview(notebook_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Personalizar las pestañas
        self.notebook.configure(
            segmented_button_fg_color=COLORES["color3"],
            segmented_button_selected_color=COLORES["color1"],
            segmented_button_selected_hover_color=COLORES["texto_oscuro"],
            text_color=COLORES["texto_oscuro"]
        )
        
        plan = generar_plan_personalizado(self.perfil_actual)
        self.mostrar_plan_en_interfaz(plan)
        
        self.mostrar_estadisticas_inferiores()
    
    def mostrar_plan_en_interfaz(self, plan):
        for semestre_num, materias_sem in plan:
            tab_name = f"📘 Semestre {semestre_num}"
            self.notebook.add(tab_name)
            
            tab = self.notebook.tab(tab_name)
            tab.configure(fg_color=COLORES["color5"])
            
            # Título del semestre
            materias_perfil = obtener_materias_por_perfil(self.perfil_actual)
            creditos_sem = sum(materias_perfil[cod]['creditos'] for cod in materias_sem)
            
            title_frame = ctk.CTkFrame(tab, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, 15))
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=f"SEMESTRE {semestre_num} - {creditos_sem} CRÉDITOS",
                font=FUENTE_TITULOS,
                text_color=COLORES["texto_oscuro"]
            )
            title_label.pack(anchor="w")
            
            # Scrollable frame para materias
            scroll_frame = ctk.CTkScrollableFrame(tab)
            scroll_frame.pack(fill="both", expand=True)
            
            for codigo in materias_sem:
                materias_perfil = obtener_materias_por_perfil(self.perfil_actual)
                materia = materias_perfil[codigo]
                
                # Card para cada materia
                mat_card = ctk.CTkFrame(
                    scroll_frame,
                    border_width=1,
                    border_color=COLORES["color3"],
                    corner_radius=10,
                    fg_color=COLORES["color4"]
                )
                mat_card.pack(fill="x", pady=5, padx=5)
                
                content_frame = ctk.CTkFrame(mat_card, fg_color="transparent")
                content_frame.pack(fill="x", padx=15, pady=10)
                
                # Código y nombre
                cod_label = ctk.CTkLabel(
                    content_frame,
                    text=f"📝 {codigo}",
                    font=FUENTE_TITULOS,
                    text_color=COLORES["texto_oscuro"]
                )
                cod_label.pack(anchor="w")
                
                nom_label = ctk.CTkLabel(
                    content_frame,
                    text=materia['nombre'],
                    font=FUENTE_NORMAL,
                    wraplength=800,
                    justify="left",
                    text_color=COLORES["texto_claro"]
                )
                nom_label.pack(anchor="w", pady=(2, 0))
                
                # Información adicional
                info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                info_frame.pack(anchor="w", pady=(8, 0))
                
                cred_label = ctk.CTkLabel(
                    info_frame,
                    text=f"🎯 {materia['creditos']} créditos",
                    font=FUENTE_PEQUEÑA,
                    text_color=COLORES["texto_claro"]
                )
                cred_label.pack(side="left", padx=(0, 15))
                
                if materia['prereq']:
                    prereq_text = f"🔗 Prereq: {', '.join(materia['prereq'])}"
                else:
                    prereq_text = "✅ Sin prerequisitos"
                
                prereq_label = ctk.CTkLabel(
                    info_frame,
                    text=prereq_text,
                    font=FUENTE_PEQUEÑA,
                    text_color=COLORES["texto_claro"]
                )
                prereq_label.pack(side="left")
    
    def mostrar_estadisticas_inferiores(self):
        stats_frame = ctk.CTkFrame(
            self.main_frame, 
            height=60,
            fg_color=COLORES["color3"],
            border_width=2,
            border_color=COLORES["color1"]
        )
        stats_frame.pack(fill="x", pady=(15, 0))
        stats_frame.pack_propagate(False)
        
        materias_perfil = obtener_materias_por_perfil(self.perfil_actual)
        total_materias = len(materias_perfil)
        materias_vistas = len(self.perfil_actual.materias_vistas)
        materias_faltantes = total_materias - materias_vistas
        total_creditos = sum(materia['creditos'] for materia in materias_perfil.values())
        creditos_vistos = sum(materias_perfil[cod]['creditos'] for cod in self.perfil_actual.materias_vistas)
        porcentaje = (materias_vistas / total_materias) * 100 if total_materias > 0 else 0
        
        proyecto_texto = "con Proyecto de Grado" if self.perfil_actual.incluir_proyecto_grado else "sin Proyecto de Grado"
        stats_text = f"📊 PROGRESO {proyecto_texto}: {materias_vistas}/{total_materias} materias ({porcentaje:.1f}%) | 🎯 {creditos_vistos}/{total_creditos} créditos | ⏳ Faltan: {materias_faltantes} materias"
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        stats_label.pack(expand=True)
    
    def mostrar_editor_materias(self):
        editor_window = ctk.CTkToplevel(self.root)
        editor_window.title(f"✏️ Editor de Materias - {self.perfil_actual.nombre}")
        editor_window.geometry("1100x750")
        editor_window.transient(self.root)
        editor_window.grab_set()
        
        # Configurar fondo de la ventana
        editor_window.configure(fg_color=COLORES["color5"])
        
        main_frame = ctk.CTkFrame(editor_window, fg_color=COLORES["color5"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        proyecto_texto = "con Proyecto de Grado" if self.perfil_actual.incluir_proyecto_grado else "sin Proyecto de Grado"
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"✏️ EDITANDO MATERIAS VISTAS - {self.perfil_actual.nombre} ({proyecto_texto})",
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        title_label.pack(pady=(0, 15))
        
        # Scrollable frame para semestres
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=COLORES["color4"],
            border_width=2,
            border_color=COLORES["color3"]
        )
        scroll_frame.pack(fill="both", expand=True)
        
        self.mostrar_semestres_colapsables(scroll_frame)
        
        # Botones de acción
        button_frame = ctk.CTkFrame(
            main_frame, 
            height=60,
            fg_color=COLORES["color3"]
        )
        button_frame.pack(fill="x", pady=(15, 0))
        button_frame.pack_propagate(False)
        
        aplicar_btn = ctk.CTkButton(
            button_frame,
            text="✅ Aplicar Cambios y Regenerar",
            command=lambda: self.aplicar_cambios_editor(editor_window),
            fg_color=COLORES["color1"],
            hover_color=COLORES["texto_oscuro"],
            height=40,
            font=FUENTE_NORMAL,
            text_color=COLORES["color5"]
        )
        aplicar_btn.pack(side="left", padx=10, pady=10)
        
        cancelar_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancelar",
            command=editor_window.destroy,
            fg_color=COLORES["color2"],
            hover_color=COLORES["color1"],
            height=40,
            font=FUENTE_NORMAL
        )
        cancelar_btn.pack(side="right", padx=10, pady=10)
    
    def mostrar_semestres_colapsables(self, parent):
        self.checkboxes_editor = {}
        self.semestres_expandidos = {}
        semestres_perfil = obtener_semestres_por_perfil(self.perfil_actual)
        
        for semestre_num, materias_sem in semestres_perfil.items():
            # Frame colapsable para cada semestre
            sem_card = ctk.CTkFrame(
                parent,
                border_width=2,
                border_color=COLORES["color1"],
                corner_radius=12,
                fg_color=COLORES["color5"]
            )
            sem_card.pack(fill="x", pady=8, padx=5)
            
            # Header del semestre
            header_frame = ctk.CTkFrame(sem_card, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=10)
            
            # Botón de expandir/colapsar
            toggle_btn = ctk.CTkButton(
                header_frame,
                text=f"📘 SEMESTRE {semestre_num}",
                font=FUENTE_TITULOS,
                fg_color="transparent",
                hover_color=COLORES["color4"],
                text_color=COLORES["texto_oscuro"],
                anchor="w",
                command=lambda sn=semestre_num: self.toggle_semestre(sn)
            )
            toggle_btn.pack(side="left", fill="x", expand=True)
            
            # Contador de materias vistas
            materias_vistas_sem = sum(1 for cod in materias_sem.keys() if cod in self.perfil_actual.materias_vistas)
            count_label = ctk.CTkLabel(
                header_frame,
                text=f"({materias_vistas_sem}/{len(materias_sem)} vistas)",
                font=FUENTE_NORMAL,
                text_color=COLORES["texto_claro"]
            )
            count_label.pack(side="right", padx=(10, 0))
            
            # Frame para contenido (inicialmente visible)
            content_frame = ctk.CTkFrame(sem_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=10)
            
            self.semestres_expandidos[semestre_num] = {
                'content_frame': content_frame,
                'expanded': True
            }
            
            # Grid para materias
            for i, (codigo, materia) in enumerate(materias_sem.items()):
                self.agregar_materia_al_editor(content_frame, codigo, materia, i)
    
    def toggle_semestre(self, semestre_num):
        estado = self.semestres_expandidos[semestre_num]
        
        if estado['expanded']:
            estado['content_frame'].pack_forget()
            estado['expanded'] = False
        else:
            estado['content_frame'].pack(fill="x", padx=15, pady=10)
            estado['expanded'] = True
    
    def agregar_materia_al_editor(self, parent, codigo, materia, index):
        # Frame para cada materia
        mat_frame = ctk.CTkFrame(
            parent, 
            corner_radius=8,
            fg_color=COLORES["color4"]
        )
        mat_frame.pack(fill="x", pady=2)
        
        # Checkbox
        var = ctk.BooleanVar(value=(codigo in self.perfil_actual.materias_vistas))
        checkbox = ctk.CTkCheckBox(
            mat_frame,
            text="",
            variable=var,
            command=lambda c=codigo, v=var: self.toggle_materia_editor(c, v),
            width=20,
            fg_color=COLORES["color1"],
            hover_color=COLORES["texto_oscuro"],
            checkmark_color=COLORES["color5"]
        )
        checkbox.pack(side="left", padx=15, pady=10)
        self.checkboxes_editor[codigo] = var
        
        # Información de la materia
        info_frame = ctk.CTkFrame(mat_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        # Código y nombre
        cod_label = ctk.CTkLabel(
            info_frame,
            text=f"📝 {codigo}",
            font=FUENTE_TITULOS,
            text_color=COLORES["texto_oscuro"]
        )
        cod_label.pack(anchor="w")
        
        nom_label = ctk.CTkLabel(
            info_frame,
            text=materia['nombre'],
            font=FUENTE_NORMAL,
            wraplength=700,
            justify="left",
            text_color=COLORES["texto_claro"]
        )
        nom_label.pack(anchor="w", pady=(2, 0))
        
        # Detalles adicionales
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(anchor="w", pady=(5, 0))
        
        cred_label = ctk.CTkLabel(
            details_frame,
            text=f"🎯 {materia['creditos']} créditos",
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["texto_claro"]
        )
        cred_label.pack(side="left", padx=(0, 15))
        
        if materia['prereq']:
            prereq_text = f"🔗 Prereq: {', '.join(materia['prereq'])}"
        else:
            prereq_text = "✅ Sin prerequisitos"
        
        prereq_label = ctk.CTkLabel(
            details_frame,
            text=prereq_text,
            font=FUENTE_PEQUEÑA,
            text_color=COLORES["texto_claro"]
        )
        prereq_label.pack(side="left")
    
    def toggle_materia_editor(self, codigo, var):
        if var.get():
            self.perfil_actual.materias_vistas.add(codigo)
        else:
            self.perfil_actual.materias_vistas.discard(codigo)
    
    def aplicar_cambios_editor(self, editor_window):
        self.perfil_actual.fecha_actualizacion = datetime.now().isoformat()
        guardar_perfiles(self.perfiles)
        editor_window.destroy()
        self.mostrar_plan_estudios_automatico()
        
        ctk.CTkMessageBox(
            title="Éxito",
            message="Plan regenerado con los nuevos cambios",
            icon="check"
        )
    
    def guardar_y_regenerar(self):
        self.perfil_actual.fecha_actualizacion = datetime.now().isoformat()
        guardar_perfiles(self.perfiles)
        self.mostrar_plan_estudios_automatico()
        
        ctk.CTkMessageBox(
            title="Éxito",
            message="Plan guardado y regenerado",
            icon="check"
        )
    
    def limpiar_pantalla(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = PlanEstudiosApp(root)
    root.mainloop()