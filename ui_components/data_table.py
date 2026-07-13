"""
ui_components/data_table.py
---------------------------
Envoltorio de ttk.Treeview con estilo oscuro y columnas que se
redimensionan dinámicamente según el ancho de la ventana.

Uso:
    columns = [
        {"key": "num",   "title": "#",          "weight": 1, "anchor": "center"},
        {"key": "name",  "title": "CIENTÍFICO", "weight": 4, "anchor": "w"},
        ...
    ]
    table = DataTable(parent, columns)
    table.load_rows(list_de_dicts)
    row = table.get_selected_row()   # dict original o None
"""

from tkinter import ttk

import customtkinter as ctk

import theme


class DataTable(ctk.CTkFrame):
    def __init__(self, master, columns, **kwargs):
        super().__init__(
            master,
            fg_color=theme.BG_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDER,
            **kwargs,
        )
        self.columns = columns
        self._rows = {}          # iid -> dict de la fila original
        self._total_weight = sum(c.get("weight", 1) for c in columns)

        keys = [c["key"] for c in columns]
        self.tree = ttk.Treeview(
            self, columns=keys, show="headings",
            style="Dark.Treeview", selectmode="browse",
        )
        for col in columns:
            self.tree.heading(col["key"], text=col["title"])
            self.tree.column(
                col["key"],
                anchor=col.get("anchor", "w"),
                width=col.get("min", 80),
                minwidth=col.get("min", 60),
                stretch=True,
            )

        self.vsb = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview,
            style="Dark.Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree.pack(side="left", fill="both", expand=True,
                       padx=(10, 0), pady=10)
        self.vsb.pack(side="right", fill="y", padx=(0, 6), pady=10)

        # Zebra striping sutil + tag de resaltado (columna espectral, etc.)
        self.tree.tag_configure("even", background=theme.BG_PANEL)
        self.tree.tag_configure("odd", background="#101828")
        self.tree.tag_configure("accent", foreground=theme.ACCENT)

        # Redimensionado dinámico de columnas
        self.tree.bind("<Configure>", self._on_resize)

    # ------------------------------------------------------------ #
    def _on_resize(self, event):
        width = max(event.width - 4, 200)
        for col in self.columns:
            w = int(width * col.get("weight", 1) / self._total_weight)
            self.tree.column(col["key"], width=max(w, col.get("min", 50)))

    # ------------------------------------------------------------ #
    def clear(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._rows = {}

    def load_rows(self, rows, formatter=None, row_tags=None):
        """
        rows      : lista de dicts (resultado de fetch_all).
        formatter : fn(dict, index) -> tupla de valores en el orden de columnas.
        row_tags  : fn(dict) -> tags extra para la fila.
        """
        self.clear()
        for i, row in enumerate(rows):
            if formatter is not None:
                values = formatter(row, i)
            else:
                values = tuple(row.get(c["key"], "") for c in self.columns)

            tags = ["even" if i % 2 == 0 else "odd"]
            if row_tags is not None:
                extra = row_tags(row)
                if extra:
                    tags.extend(extra)

            iid = self.tree.insert("", "end", values=values, tags=tags)
            self._rows[iid] = row

    def get_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self._rows.get(sel[0])
