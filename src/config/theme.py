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
    "bg_deep":     "#0d0f1a",   # Fondo más profundo de la ventana
    "bg_card":     "#161929",   # Fondo de cards y paneles secundarios
    "bg_elevated": "#1e2235",   # Elementos elevados: headers, navbar
    "bg_hover":    "#252840",   # Estado hover de botones neutros

    # Acentos principales
    "accent_primary":   "#7c6fff",  # Morado principal — CTA, selección activa
    "accent_glow":      "#9b8fff",  # Morado claro — hover sobre accent_primary
    "accent_success":   "#10d9a0",  # Verde azulado — aprobado / éxito
    "accent_warning":   "#f59e0b",  # Ámbar — alertas, prerequisitos
    "accent_danger":    "#ef4444",  # Rojo — eliminar / acciones destructivas

    # Texto (jerarquía)
    "text_primary":   "#eeeef8",  # Texto principal (casi blanco)
    "text_secondary": "#a0a8c0",  # Texto secundario (gris azulado)
    "text_muted":     "#636b85",  # Texto muy tenue / placeholder

    # Bordes
    "border_subtle": "#252840",   # Separador suave entre secciones
    "border_active": "#7c6fff",   # Borde enfocado / resaltado
}

# ── Fuentes — jerarquía tipográfica ────────────────────────────────────────
# Segoe UI es la fuente del sistema en Windows: limpia, moderna y con buen soporte Unicode.
FUENTE_H1      = ("Segoe UI", 20, "bold")   # Título principal de pantalla
FUENTE_H2      = ("Segoe UI", 15, "bold")   # Subtítulos, nombres de sección
FUENTE_NORMAL  = ("Segoe UI", 13)           # Cuerpo de texto estándar
FUENTE_PEQUEÑA = ("Segoe UI", 11)           # Etiquetas pequeñas, badges, metadata

# ── Íconos Vectoriales Nativos (Segoe MDL2 Assets / Segoe Fluent Icons) ─────
# Se utilizan caracteres PUA de la fuente de iconos nativa de Windows para evitar
# los emojis inconsistentes de Tkinter y mostrar símbolos estilizados del color del tema.
GLYPHS: dict[str, str] = {
    "cap": "\uE7BE",        # Birrete / Educación
    "user": "\uE77B",       # Usuario / Contacto
    "empty": "\uE10F",      # Buzón vacío / Bandeja de entrada
    "folder": "\uE8B7",     # Carpeta
    "sparkles": "\uE734",   # Estrella / Nuevo
    "trash": "\uE74D",      # Papelera / Borrar
    "calendar": "\uE787",   # Calendario
    "plan": "\uE8A5",       # Documento / Plan
    "edit": "\uE70F",       # Lápiz / Editar
    "save": "\uE74E",       # Disquete / Guardar
    "book": "\uE736",       # Libro abierto / Semestre
    "memo": "\uE943",       # Documento de texto / Materia
    "target": "\uE7C9",     # Blanco / Créditos
    "link": "\uE71B",       # Eslabón / Prerrequisito
    "check": "\uE73E",      # Marca de verificación / Aprobado
    "back": "\uE72B",       # Flecha izquierda / Volver
    "warning": "\uE7BA",    # Triángulo de advertencia / Advertencia
    "cancel": "\uE711",     # Cruz / Cancelar
    "sparkle_small": "\uE99A", # Chispas pequeñas
}

