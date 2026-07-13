"""
main.py
-------
Orquestador principal de la aplicación.

Flujo:
    1. LoginView  -> el usuario elige sede ("chile" | "espana").
    2. Se instancia DBConnection ligada al nodo.
    3. Se levanta la shell principal (Sidebar + Topbar + área de contenido).
    4. El ruteo de vistas se resuelve con if/elif/else (SIN match-case):
         - "observaciones" carga ObservationsChile u ObservationsSpain
           según self.sede.

Ejecutar:  python main.py
"""

import customtkinter as ctk

import theme
from config import APP_NAME, NODES
from ui_components.catalog_views import (
    AsteroidesView, CientificosView, ObservatoriosView,
    ParticipacionesView, ProgramasView,
)
from ui_components.login_view import LoginView
from ui_components.observations_chile import ObservationsChile
from ui_components.observations_spain import ObservationsSpain
from ui_components.sidebar import Sidebar
from ui_components.topbar import Topbar

ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=theme.BG_MAIN)
        self.title(APP_NAME)
        self.geometry("1360x800")
        self.minsize(1100, 680)

        theme.setup_treeview_style(self)

        # Estado de sesión
        self.sede = None          # "chile" | "espana"
        self.usuario = None
        self.db = None

        self._current_view = None
        self._show_login()

    # ================================================================ #
    # LOGIN
    # ================================================================ #
    def _show_login(self):
        self._clear_root()
        self.login = LoginView(self, on_login=self._on_login)
        self.login.pack(fill="both", expand=True)

    def _on_login(self, sede, usuario, db):
        self.sede = sede
        self.usuario = usuario
        self.db = db
        self._build_shell()

    def _logout(self):
        self.sede = None
        self.usuario = None
        self.db = None
        self._current_view = None
        self._show_login()

    def _clear_root(self):
        for child in self.winfo_children():
            child.destroy()

    # ================================================================ #
    # SHELL PRINCIPAL (Sidebar + Topbar + Contenido)
    # ================================================================ #
    def _build_shell(self):
        self._clear_root()
        cfg = NODES[self.sede]

        self.sidebar = Sidebar(self, sede_cfg=cfg,
                               on_navigate=self.navigate,
                               on_logout=self._logout)
        self.sidebar.pack(side="left", fill="y")

        # Separador vertical
        ctk.CTkFrame(self, width=1, fg_color=theme.BORDER,
                     corner_radius=0).pack(side="left", fill="y")

        right = ctk.CTkFrame(self, fg_color=theme.BG_MAIN, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self.topbar = Topbar(right, sede_cfg=cfg, usuario=self.usuario)
        self.topbar.pack(fill="x")

        ctk.CTkFrame(right, height=1, fg_color=theme.BORDER,
                     corner_radius=0).pack(fill="x")

        self.content = ctk.CTkFrame(right, fg_color=theme.BG_MAIN,
                                    corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=24, pady=20)

        # Vista inicial: dashboard de observaciones
        self.sidebar.set_active("observaciones")
        self.navigate("observaciones")

    # ================================================================ #
    # RUTEO DE VISTAS — if/elif/else (match-case prohibido)
    # ================================================================ #
    def navigate(self, route):
        if self._current_view is not None:
            self._current_view.destroy()
            self._current_view = None

        if route == "observaciones":
            # ---- Bifurcación dinámica por sede seleccionada en Login ----
            if self.sede == "chile":
                view = ObservationsChile(self.content, self.db)
            elif self.sede == "espana":
                view = ObservationsSpain(self.content, self.db)
            else:
                raise RuntimeError(f"Sede inválida: {self.sede!r}")

        elif route == "asteroides":
            view = AsteroidesView(self.content, self.db)

        elif route == "cientificos":
            view = CientificosView(self.content, self.db)

        elif route == "participaciones":
            view = ParticipacionesView(self.content, self.db)

        elif route == "programas":
            view = ProgramasView(self.content, self.db)

        elif route == "observatorios":
            view = ObservatoriosView(self.content, self.db)

        else:
            raise RuntimeError(f"Ruta desconocida: {route!r}")

        self.topbar.set_title(view.view_title)
        view.pack(fill="both", expand=True)
        self._current_view = view


if __name__ == "__main__":
    app = App()
    app.mainloop()
