"""
ui_components/form_modal.py
---------------------------
Formulario modal genérico basado en ctk.CTkToplevel:
  - Centrado sobre la ventana principal.
  - grab_set() para bloquear la ventana padre.
  - Campos declarativos: entry | dropdown.

Especificación de campo:
    {
        "key": "Nombre",            # clave del dict resultante
        "label": "Nombre",          # etiqueta visible
        "widget": "entry"|"dropdown",
        "values": [...],            # solo dropdown
        "default": "...",           # valor inicial
        "mono": True|False,         # usa JetBrains Mono (IDs, fechas...)
        "readonly": True|False,     # deshabilitado (claves en UPDATE)
        "required": True|False,     # validación de no vacío (default True)
        "placeholder": "...",
    }
"""

from tkinter import messagebox

import customtkinter as ctk

import theme


class FormModal(ctk.CTkToplevel):
    def __init__(self, master, title, fields, on_submit,
                 submit_text="GUARDAR", subtitle=None):
        super().__init__(master, fg_color=theme.BG_PANEL)
        self.title(title)
        self.resizable(False, False)
        self.configure(border_width=1, border_color=theme.BORDER)

        self._fields = fields
        self._on_submit = on_submit
        self._widgets = {}

        # ---------- Encabezado ----------
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            head, text=title.upper(), font=theme.mono_font(15, "bold"),
            text_color=theme.ACCENT,
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                head, text=subtitle, font=theme.ui_font(12),
                text_color=theme.TEXT_SEC,
            ).pack(anchor="w", pady=(2, 0))

        # ---------- Cuerpo ----------
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=12)

        for field in fields:
            ctk.CTkLabel(
                body, text=field["label"].upper(),
                font=theme.mono_font(10, "bold"),
                text_color=theme.TEXT_SEC,
            ).pack(anchor="w", pady=(10, 3))

            widget_type = field.get("widget", "entry")
            font = theme.mono_font(13) if field.get("mono") else theme.ui_font(13)

            if widget_type == "dropdown":
                var = ctk.StringVar(value=field.get("default",
                                                    field["values"][0]))
                widget = ctk.CTkOptionMenu(
                    body, values=field["values"], variable=var, width=340,
                    fg_color=theme.BG_MAIN, button_color=theme.BORDER,
                    button_hover_color=theme.ACCENT_DIM,
                    dropdown_fg_color=theme.BG_PANEL,
                    dropdown_hover_color=theme.ACCENT_DIM,
                    dropdown_text_color=theme.TEXT_MAIN,
                    text_color=theme.TEXT_MAIN, font=font,
                    dropdown_font=font,
                )
                widget.pack(fill="x")
                self._widgets[field["key"]] = ("dropdown", var, widget)
            else:
                widget = ctk.CTkEntry(
                    body, width=340, height=36,
                    fg_color=theme.BG_MAIN, border_color=theme.BORDER,
                    border_width=1, text_color=theme.TEXT_MAIN, font=font,
                    placeholder_text=field.get("placeholder", ""),
                )
                default = field.get("default")
                if default is not None and default != "":
                    widget.insert(0, str(default))
                if field.get("readonly"):
                    widget.configure(state="disabled",
                                     text_color=theme.TEXT_SEC)
                widget.pack(fill="x")
                self._widgets[field["key"]] = ("entry", None, widget)

        # ---------- Botonera ----------
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=28, pady=(8, 24))

        ctk.CTkButton(
            footer, text="CANCELAR", width=120, height=38,
            fg_color="transparent", hover_color=theme.BORDER,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SEC, font=theme.mono_font(12, "bold"),
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            footer, text=submit_text, width=170, height=38,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOV,
            text_color=theme.BG_MAIN, font=theme.mono_font(12, "bold"),
            command=self._submit,
        ).pack(side="right")

        # ---------- Modalidad + centrado ----------
        self.transient(master)
        self.update_idletasks()
        self._center_on(master)
        self.grab_set()          # Bloquea la ventana principal
        self.focus_force()
        self.bind("<Escape>", lambda _e: self.destroy())

    # ------------------------------------------------------------ #
    def _center_on(self, master):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        mx, my = master.winfo_rootx(), master.winfo_rooty()
        mw, mh = master.winfo_width(), master.winfo_height()
        x = mx + (mw - w) // 2
        y = my + (mh - h) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------------ #
    def _collect(self):
        data = {}
        for field in self._fields:
            kind, var, widget = self._widgets[field["key"]]
            if kind == "dropdown":
                value = var.get()
            else:
                value = widget.get().strip()

            if field.get("required", True) and value == "":
                raise ValueError(
                    f"El campo '{field['label']}' es obligatorio.")
            data[field["key"]] = value
        return data

    def _submit(self):
        try:
            data = self._collect()
        except ValueError as exc:
            messagebox.showwarning("Validación", str(exc), parent=self)
            return

        # on_submit devuelve True si la operación en BD fue exitosa.
        ok = self._on_submit(data, self)
        if ok:
            self.destroy()
