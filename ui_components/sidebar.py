"""
ui_components/sidebar.py
------------------------
Barra lateral de navegación. Ruteo con if/elif/else (sin match-case):
el callback `on_navigate(route)` es resuelto por main.py.
"""

import customtkinter as ctk

import theme


NAV_ITEMS = [
    ("observaciones",   "◉  OBSERVACIONES"),
    ("asteroides",      "☄  ASTEROIDES"),
    ("cientificos",     "⌬  CIENTÍFICOS"),
    ("participaciones", "⛓  PARTICIPACIONES"),
    ("programas",       "▤  PROGRAMAS"),
    ("observatorios",   "⌖  OBSERVATORIOS"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, sede_cfg, on_navigate, on_logout):
        super().__init__(
            master, width=250, corner_radius=0,
            fg_color=theme.BG_PANEL,
            border_width=0,
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self._buttons = {}

        # ---------- Logo ----------
        logo = ctk.CTkFrame(self, fg_color="transparent")
        logo.pack(fill="x", padx=22, pady=(26, 6))
        ctk.CTkLabel(logo, text="NASA / PDCO",
                     font=theme.mono_font(17, "bold"),
                     text_color=theme.TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(logo, text="PLANETARY DEFENSE\nDISTRIBUTED DATABASE",
                     font=theme.mono_font(9), justify="left",
                     text_color=theme.TEXT_SEC).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(self, height=1, fg_color=theme.BORDER
                     ).pack(fill="x", padx=18, pady=14)

        # ---------- Navegación ----------
        for route, label in NAV_ITEMS:
            btn = ctk.CTkButton(
                self, text=label, anchor="w", height=40, corner_radius=8,
                fg_color="transparent", hover_color=theme.ACCENT_DIM,
                text_color=theme.TEXT_SEC, font=theme.ui_font(13),
                command=lambda r=route: self._navigate(r),
            )
            btn.pack(fill="x", padx=14, pady=3)
            self._buttons[route] = btn

        # ---------- Pie: badge del nodo + logout ----------
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=14, pady=18)

        badge = ctk.CTkFrame(footer, fg_color=theme.BG_MAIN,
                             corner_radius=10, border_width=1,
                             border_color=theme.BORDER)
        badge.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(badge, text="● NODO ACTIVO",
                     font=theme.mono_font(9, "bold"),
                     text_color=theme.OK).pack(anchor="w", padx=12,
                                               pady=(8, 0))
        ctk.CTkLabel(badge, text=sede_cfg["short"],
                     font=theme.mono_font(11, "bold"),
                     text_color=theme.ACCENT).pack(anchor="w", padx=12,
                                                   pady=(0, 8))

        ctk.CTkButton(
            footer, text="⏻  CERRAR SESIÓN", height=34, corner_radius=8,
            fg_color="transparent", hover_color=theme.BORDER,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SEC, font=theme.mono_font(11),
            command=on_logout,
        ).pack(fill="x")

    # ------------------------------------------------------------ #
    def _navigate(self, route):
        self.set_active(route)
        self.on_navigate(route)

    def set_active(self, route):
        for r, btn in self._buttons.items():
            if r == route:
                btn.configure(fg_color=theme.ACCENT_DIM,
                              text_color=theme.ACCENT)
            else:
                btn.configure(fg_color="transparent",
                              text_color=theme.TEXT_SEC)
