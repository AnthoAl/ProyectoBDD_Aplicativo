"""
ui_components/sede_filter_mixin.py
-----------------------------------
Mixin reutilizable para vistas CRUD sobre fragmentos horizontales
(Observaciones, Científicos, Participaciones): agrega una barra de
filtro CHILE / ESPAÑA / AMBAS SEDES que solo controla qué se MUESTRA,
apoyada en las vistas particionadas globales (VistaGlobalObservaciones,
VistaGlobalCientificos, VistaGlobalParticipaciones).

Uso en una subclase de BaseCrudView:

    class MiVista(SedeFilterMixin, BaseCrudView):
        def __init__(self, master, db):
            self._init_sede_filter(db)
            super().__init__(master, db, self.COLUMNS)

        def fetch_rows(self):
            return mi_modelo.get_algo(self.db, self.filtro)

Las escrituras (AGREGAR/MODIFICAR/BORRAR) siguen las reglas propias de
cada fragmento y SIEMPRE apuntan al nodo local conectado (self.db.sede);
el filtro de este mixin es solo de lectura. `can_modify()` veta
modificar/borrar filas que pertenecen a un nodo distinto al conectado.
"""

import customtkinter as ctk

import theme

FILTROS_SEDE = [
    ("chile", "CHILE"),
    ("espana", "ESPAÑA"),
    ("ambas", "AMBAS SEDES"),
]


class SedeFilterMixin:
    def _init_sede_filter(self, db):
        self._filtro_buttons = {}
        # Por defecto se muestra el nodo local del operador conectado.
        self.filtro = db.sede

    # ------------------- Filtro de sede (barra extra) ------------------- #
    def build_extra_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(bar, text="SEDE:", font=theme.mono_font(11, "bold"),
                     text_color=theme.TEXT_SEC).pack(side="left", padx=(0, 8))

        for key, label in FILTROS_SEDE:
            btn = ctk.CTkButton(
                bar, text=label, height=30, width=120, corner_radius=8,
                border_width=1, font=theme.mono_font(10, "bold"),
                command=lambda k=key: self._set_filtro(k),
            )
            btn.pack(side="left", padx=(0, 6))
            self._filtro_buttons[key] = btn

        self._refresh_filtro_buttons()
        return bar

    def _set_filtro(self, key):
        if key == self.filtro:
            return
        self.filtro = key
        self._refresh_filtro_buttons()
        self.refresh()

    def _refresh_filtro_buttons(self):
        for key, btn in self._filtro_buttons.items():
            if key == self.filtro:
                btn.configure(fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOV,
                              text_color=theme.BG_MAIN, border_color=theme.ACCENT)
            else:
                btn.configure(fg_color="transparent", hover_color=theme.BORDER,
                              text_color=theme.TEXT_SEC, border_color=theme.BORDER)

    # ---------------- Permisos de escritura por fila ---------------- #
    def can_modify(self, row):
        # Solo se puede modificar/borrar lo que pertenece al nodo local
        # conectado (evita escribir sobre el fragmento de otra sede).
        return row.get("Id_Observatorio") == self.db.cfg["id_observatorio"]