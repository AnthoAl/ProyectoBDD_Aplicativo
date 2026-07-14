"""
ui_components/base_crud_view.py
-------------------------------
Vista CRUD genérica y reutilizable:

    Toolbar [ + AGREGAR | ✎ MODIFICAR | 🗑 BORRAR | ⟳ REFRESCAR ]
    DataTable (ttk.Treeview oscuro)
    Barra de estado

Flujo:
    READ    -> refresh() vacía el Treeview y vuelve a consultar SQL Server.
    CREATE  -> modal FormModal + INSERT + refresh().
    UPDATE  -> modal precargado + UPDATE + refresh().
    DELETE  -> messagebox de confirmación + DELETE + refresh().

Las subclases (u orquestador) proveen:
    columns        : especificación de columnas del DataTable
    fetch_rows()   : lista de dicts
    build_fields(row|None) : campos del FormModal
    do_insert(data), do_update(row, data), do_delete(row)
    format_row(row, i) (opcional), row_tags(row) (opcional)
"""

from tkinter import messagebox

import customtkinter as ctk

import theme
from db_connection import DBError
from ui_components.data_table import DataTable
from ui_components.form_modal import FormModal


class BaseCrudView(ctk.CTkFrame):
    view_title = "VISTA"
    entity_name = "registro"

    def __init__(
        self, master, db, columns, allow_edit=True, allow_create=True, allow_delete=True
    ):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.columns = columns

        # Parámetros de permisos CRUD
        self.allow_edit = allow_edit
        self.allow_create = allow_create
        self.allow_delete = allow_delete

        # ---------------- Toolbar ----------------
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))

        def make_btn(text, command, accent=False, danger=False):
            if danger:
                fg, hover, txt = "transparent", theme.DANGER_HOV, theme.DANGER
                border = theme.DANGER
            elif accent:
                fg, hover, txt = theme.ACCENT, theme.ACCENT_HOV, theme.BG_MAIN
                border = theme.ACCENT
            else:
                fg, hover, txt = "transparent", theme.BORDER, theme.TEXT_SEC
                border = theme.BORDER
            return ctk.CTkButton(
                toolbar,
                text=text,
                height=36,
                corner_radius=8,
                width=140,
                fg_color=fg,
                hover_color=hover,
                text_color=txt,
                border_width=1,
                border_color=border,
                font=theme.mono_font(11, "bold"),
                command=command,
            )

        if self.allow_create:
            make_btn("＋ AGREGAR", self._on_add, accent=True).pack(
                side="left", padx=(0, 8)
            )

        if self.allow_edit:
            make_btn("✎ MODIFICAR", self._on_edit).pack(side="left", padx=(0, 8))

        if self.allow_delete:
            make_btn("🗑 BORRAR", self._on_delete, danger=True).pack(
                side="left", padx=(0, 8)
            )

        make_btn("⟳ REFRESCAR", self.refresh).pack(side="left")

        self.lbl_status = ctk.CTkLabel(
            toolbar,
            text="",
            font=theme.mono_font(10),
            text_color=theme.TEXT_SEC,
        )
        self.lbl_status.pack(side="right", padx=6)

        # ---------------- Tabla ----------------
        self.table = DataTable(self, columns)
        self.table.pack(fill="both", expand=True)

        self.refresh()

    # ================= Hooks a implementar ================= #
    def fetch_rows(self):
        raise NotImplementedError

    def build_fields(self, row=None):
        raise NotImplementedError

    def do_insert(self, data):
        raise NotImplementedError

    def do_update(self, row, data):
        raise NotImplementedError

    def do_delete(self, row):
        raise NotImplementedError

    def format_row(self, row, index):
        return tuple(row.get(c["key"], "") for c in self.columns)

    def row_tags(self, row):
        return None

    # ================= READ + refresco automático ================= #
    def refresh(self):
        try:
            rows = self.fetch_rows()
        except DBError as exc:
            messagebox.showerror(
                "Error de base de datos", str(exc), parent=self.winfo_toplevel()
            )
            return
        self.table.load_rows(rows, formatter=self.format_row, row_tags=self.row_tags)
        self.lbl_status.configure(
            text=f"{len(rows)} REGISTROS · NODO {self.db.cfg['short']}"
        )

    # ================= CREATE ================= #
    def _on_add(self):
        def submit(data, modal):
            try:
                self.do_insert(data)
            except (DBError, ValueError) as exc:
                messagebox.showerror("Error al insertar", str(exc), parent=modal)
                return False
            self.refresh()
            return True

        FormModal(
            self.winfo_toplevel(),
            title=f"Agregar {self.entity_name}",
            subtitle=self.db.cfg["label"],
            fields=self.build_fields(None),
            on_submit=submit,
            submit_text="INSERTAR",
        )

    # ================= UPDATE ================= #
    def _on_edit(self):
        row = self.table.get_selected_row()
        if row is None:
            messagebox.showinfo(
                "Modificar",
                f"Selecciona un {self.entity_name} en la tabla.",
                parent=self.winfo_toplevel(),
            )
            return

        def submit(data, modal):
            try:
                self.do_update(row, data)
            except (DBError, ValueError) as exc:
                messagebox.showerror("Error al modificar", str(exc), parent=modal)
                return False
            self.refresh()
            return True

        FormModal(
            self.winfo_toplevel(),
            title=f"Modificar {self.entity_name}",
            subtitle=self.db.cfg["label"],
            fields=self.build_fields(row),
            on_submit=submit,
            submit_text="ACTUALIZAR",
        )

    # ================= DELETE ================= #
    def _on_delete(self):
        row = self.table.get_selected_row()
        if row is None:
            messagebox.showinfo(
                "Borrar",
                f"Selecciona un {self.entity_name} en la tabla.",
                parent=self.winfo_toplevel(),
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar definitivamente este {self.entity_name} "
            f"del nodo {self.db.cfg['short']}?\n\n"
            "Esta operación ejecutará DELETE en SQL Server.",
            icon="warning",
            parent=self.winfo_toplevel(),
        )
        if not confirm:
            return

        try:
            self.do_delete(row)
        except DBError as exc:
            messagebox.showerror(
                "Error al borrar", str(exc), parent=self.winfo_toplevel()
            )
            return
        self.refresh()
