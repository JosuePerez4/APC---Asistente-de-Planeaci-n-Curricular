"""
src/config/theme.py
===================
Configuración del tema visual de la aplicación APC.

Define la paleta de colores dark-mode, la jerarquía tipográfica
y aplica la apariencia global de customtkinter.
Todo lo visual de la app debe importar desde aquí — nunca hardcodear colores.
"""

import customtkinter as ctk

# ── Apariencia global de customtkinter ─────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ── Paleta de colores — Dark Mode moderno ──────────────────────────────────
COLORES: dict[str, str] = {
    # Fondos (de más oscuro a más claro)
    "bg_deep": "#0d0f1a",  # Fondo más profundo de la ventana
    "bg_card": "#161929",  # Fondo de cards y paneles secundarios
    "bg_elevated": "#1e2235",  # Elementos elevados: headers, navbar
    "bg_hover": "#252840",  # Estado hover de botones neutros
    # Acentos principales
    "accent_primary": "#7c6fff",  # Morado principal — CTA, selección activa
    "accent_glow": "#9b8fff",  # Morado claro — hover sobre accent_primary
    "accent_success": "#10d9a0",  # Verde azulado — aprobado / éxito
    "accent_warning": "#f59e0b",  # Ámbar — alertas, prerequisitos
    "accent_danger": "#ef4444",  # Rojo — eliminar / acciones destructivas
    # Texto (jerarquía)
    "text_primary": "#eeeef8",  # Texto principal (casi blanco)
    "text_secondary": "#a0a8c0",  # Texto secundario (gris azulado)
    "text_muted": "#636b85",  # Texto muy tenue / placeholder
    # Bordes
    "border_subtle": "#252840",  # Separador suave entre secciones
    "border_active": "#7c6fff",  # Borde enfocado / resaltado
}

# ── Fuentes — jerarquía tipográfica ────────────────────────────────────────
# Segoe UI es la fuente del sistema en Windows: limpia, moderna y con buen soporte Unicode.
FUENTE_H1 = ("Segoe UI", 20, "bold")  # Título principal de pantalla
FUENTE_H2 = ("Segoe UI", 15, "bold")  # Subtítulos, nombres de sección
FUENTE_NORMAL = ("Segoe UI", 13)  # Cuerpo de texto estándar
FUENTE_PEQUEÑA = ("Segoe UI", 11)  # Etiquetas pequeñas, badges, metadata

# ── Íconos Vectoriales Nativos (Segoe MDL2 Assets / Segoe Fluent Icons) ─────
# Se utilizan caracteres PUA de la fuente de iconos nativa de Windows para evitar
# los emojis inconsistentes de Tkinter y mostrar símbolos estilizados del color del tema.
GLYPHS: dict[str, str] = {
    "cap": "\ue7be",  # Birrete / Educación
    "user": "\ue77b",  # Usuario / Contacto
    "empty": "\ue10f",  # Buzón vacío / Bandeja de entrada
    "folder": "\ue8b7",  # Carpeta
    "sparkles": "\ue734",  # Estrella / Nuevo
    "trash": "\ue74d",  # Papelera / Borrar
    "calendar": "\ue787",  # Calendario
    "plan": "\ue8a5",  # Documento / Plan
    "edit": "\ue70f",  # Lápiz / Editar
    "save": "\ue74e",  # Disquete / Guardar
    "book": "\ue736",  # Libro abierto / Semestre
    "memo": "\ue943",  # Documento de texto / Materia
    "target": "\ue7c9",  # Blanco / Créditos
    "link": "\ue71b",  # Eslabón / Prerrequisito
    "check": "\ue73e",  # Marca de verificación / Aprobado
    "back": "\ue72b",  # Flecha izquierda / Volver
    "warning": "\ue7ba",  # Triángulo de advertencia / Advertencia
    "cancel": "\ue711",  # Cruz / Cancelar
    "sparkle_small": "\ue99a",  # Chispas pequeñas
    "import": "",  # Descargar / Importar desde el portal
}
