"""
theme.py
--------
Paleta de colores, tipografías y estilo del ttk.Treeview
según la especificación de diseño (Figma).
"""

import tkinter.font as tkfont
from tkinter import ttk

# ------------------------------------------------------------------ #
# Paleta base
# ------------------------------------------------------------------ #
BG_MAIN     = "#080c18"   # Fondo principal
BG_PANEL    = "#0e1422"   # Contenedores / modales
BORDER      = "#161d2e"   # Bordes
TEXT_MAIN   = "#e2e8f4"   # Texto principal
TEXT_SEC    = "#7a8ba0"   # Texto secundario
ACCENT      = "#00c8e8"   # Cian brillante (acciones / resaltado)
ACCENT_HOV  = "#00a6c2"
ACCENT_DIM  = "#0b384a"   # ≈ rgba(0,200,232,0.2) compuesto sobre #0e1422
DANGER      = "#e8506a"
DANGER_HOV  = "#c23a52"
OK          = "#39d98a"

FONT_UI     = "Inter"
FONT_MONO   = "JetBrains Mono"


def _resolve(family, fallback):
    """Devuelve la familia si está instalada; si no, un fallback razonable."""
    try:
        available = set(tkfont.families())
    except Exception:
        return fallback
    if family in available:
        return family
    return fallback


def ui_font(size=13, weight="normal"):
    return (_resolve(FONT_UI, "Segoe UI"), size, weight)


def mono_font(size=12, weight="normal"):
    return (_resolve(FONT_MONO, "Consolas"), size, weight)


# ------------------------------------------------------------------ #
# Estilo del ttk.Treeview (fondo oscuro, sin bordes blancos,
# selección cian translúcida)
# ------------------------------------------------------------------ #
def setup_treeview_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "Dark.Treeview",
        background=BG_PANEL,
        fieldbackground=BG_PANEL,
        foreground=TEXT_MAIN,
        bordercolor=BORDER,
        borderwidth=0,
        relief="flat",
        rowheight=34,
        font=ui_font(12),
    )
    style.map(
        "Dark.Treeview",
        background=[("selected", ACCENT_DIM)],       # rgba(0,200,232,0.2)
        foreground=[("selected", ACCENT)],
    )

    style.configure(
        "Dark.Treeview.Heading",
        background=BG_MAIN,
        foreground=TEXT_SEC,
        bordercolor=BORDER,
        borderwidth=0,
        relief="flat",
        font=mono_font(11, "bold"),
        padding=(10, 8),
    )
    style.map(
        "Dark.Treeview.Heading",
        background=[("active", BORDER)],
        foreground=[("active", ACCENT)],
    )

    # Scrollbar oscura
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=BORDER, troughcolor=BG_MAIN,
        bordercolor=BG_MAIN, arrowcolor=TEXT_SEC, relief="flat",
    )
    style.map("Dark.Vertical.TScrollbar",
              background=[("active", ACCENT_DIM)])
    return style
