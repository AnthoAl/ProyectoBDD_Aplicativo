"""
ui_components/form_modal.py
---------------------------
Formulario modal genérico.
Se corrige el bug de geometría en CTkToplevel forzando el cálculo
de tamaño (w x h) antes de bloquear la ventana.
"""

from tkinter import messagebox
from datetime import datetime, timezone
from tkcalendar import DateEntry
import customtkinter as ctk

import theme


class FormModal(ctk.CTkToplevel):
    def __init__(
        self, master, title, fields, on_submit, submit_text="GUARDAR", subtitle=None
    ):
        super().__init__(master, fg_color=theme.BG_PANEL)
        self.title(title)

        # ELIMINAMOS self.resizable(False, False) DE AQUÍ.
        # Si lo dejamos al inicio, Windows recorta la ventana antes de medir los campos.

        self.configure(border_width=1, border_color=theme.BORDER)

        self._fields = fields
        self._on_submit = on_submit
        self._widgets = {}

        # ---------- Encabezado ----------
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(
            head,
            text=title.upper(),
            font=theme.mono_font(15, "bold"),
            text_color=theme.ACCENT,
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                head,
                text=subtitle,
                font=theme.ui_font(12),
                text_color=theme.TEXT_SEC,
            ).pack(anchor="w", pady=(2, 0))

        # ---------- Cuerpo ----------
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=12)

        for field in fields:
            try:
                ctk.CTkLabel(
                    body,
                    text=field["label"].upper(),
                    font=theme.mono_font(10, "bold"),
                    text_color=theme.TEXT_SEC,
                ).pack(anchor="w", pady=(10, 3))

                widget_type = field.get("widget", "entry")
                font = theme.mono_font(13) if field.get("mono") else theme.ui_font(13)

                # 1. WIDGET DROPDOWN
                if widget_type == "dropdown":
                    var = ctk.StringVar(value=field.get("default", field["values"][0]))
                    widget = ctk.CTkOptionMenu(
                        body,
                        values=field["values"],
                        variable=var,
                        width=340,
                        fg_color=theme.BG_MAIN,
                        button_color=theme.BORDER,
                        button_hover_color=theme.ACCENT_DIM,
                        text_color=theme.TEXT_MAIN,
                        font=font,
                    )
                    widget.pack(fill="x")
                    self._widgets[field["key"]] = ("dropdown", var, widget)

                # 2. WIDGET DATETIME (Fecha y Hora - Observaciones)
                elif widget_type == "datetime":
                    container = ctk.CTkFrame(body, fg_color="transparent")
                    container.pack(fill="x")

                    date_widget = DateEntry(
                        container,
                        width=15,
                        background="#080c18",
                        foreground="white",
                        borderwidth=0,
                        headersbackground="#0e1422",
                        headersforeground="white",
                        selectbackground="#00c8e8",
                        selectforeground="black",
                        date_pattern="yyyy-mm-dd",
                        font=("Inter", 11),
                    )
                    date_widget.pack(side="left", padx=(0, 10), ipady=5)

                    time_widget = ctk.CTkEntry(
                        container,
                        width=80,
                        height=30,
                        fg_color=theme.BG_MAIN,
                        border_color=theme.BORDER,
                        text_color=theme.TEXT_MAIN,
                        font=font,
                        placeholder_text="HH:MM",
                    )
                    time_widget.pack(side="left")

                    default = field.get("default")
                    if default:
                        try:
                            dt_val = datetime.strptime(
                                str(default)[:16], "%Y-%m-%d %H:%M"
                            )
                            date_widget.set_date(dt_val.date())
                            time_widget.insert(0, dt_val.strftime("%H:%M"))
                        except ValueError:
                            pass

                    if field.get("readonly"):
                        date_widget.configure(state="disabled")
                        time_widget.configure(
                            state="disabled", text_color=theme.TEXT_SEC
                        )

                    self._widgets[field["key"]] = (
                        "datetime",
                        None,
                        (date_widget, time_widget),
                    )

                # 3. WIDGET DATE (Solo Calendario - Participaciones)
                elif widget_type == "date":
                    container = ctk.CTkFrame(body, fg_color="transparent")
                    container.pack(fill="x")

                    date_widget = DateEntry(
                        container,
                        width=15,
                        background="#080c18",
                        foreground="white",
                        borderwidth=0,
                        headersbackground="#0e1422",
                        headersforeground="white",
                        selectbackground="#00c8e8",
                        selectforeground="black",
                        date_pattern="yyyy-mm-dd",
                        font=("Inter", 12),
                    )
                    date_widget.pack(side="left", ipady=5)

                    default = field.get("default")
                    if default and str(default).strip() != "" and str(default) != "—":
                        try:
                            dt_val = datetime.strptime(str(default)[:10], "%Y-%m-%d")
                            date_widget.set_date(dt_val.date())
                        except ValueError:
                            pass

                    if field.get("readonly"):
                        date_widget.configure(state="disabled")

                    self._widgets[field["key"]] = ("date", None, date_widget)

                # 4. WIDGET ENTRY CLÁSICO
                else:
                    widget = ctk.CTkEntry(
                        body,
                        width=340,
                        height=36,
                        fg_color=theme.BG_MAIN,
                        border_color=theme.BORDER,
                        border_width=1,
                        text_color=theme.TEXT_MAIN,
                        font=font,
                        placeholder_text=field.get("placeholder", ""),
                    )
                    default = field.get("default")
                    if default is not None and default != "":
                        widget.insert(0, str(default))
                    if field.get("readonly"):
                        widget.configure(state="disabled", text_color=theme.TEXT_SEC)
                    widget.pack(fill="x")
                    self._widgets[field["key"]] = ("entry", None, widget)

            except Exception as e:
                # Defensa estructural: Si algo falla, avisa pero permite cargar los botones
                print(f"Error cargando el campo '{field.get('key')}': {str(e)}")
                ctk.CTkLabel(
                    body,
                    text=f"⚠ Fallo al cargar: {field.get('label')}",
                    text_color="#e8506a",
                ).pack(anchor="w")

        # ---------- Botonera ----------
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=28, pady=(8, 24))

        ctk.CTkButton(
            footer,
            text="CANCELAR",
            width=120,
            height=38,
            fg_color="transparent",
            hover_color=theme.BORDER,
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT_SEC,
            font=theme.mono_font(12, "bold"),
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text=submit_text,
            width=170,
            height=38,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOV,
            text_color=theme.BG_MAIN,
            font=theme.mono_font(12, "bold"),
            command=self._submit,
        ).pack(side="right")

        self.transient(master)

        # 1. Centramos la ventana SOLO usando coordenadas X e Y
        self._center_on(master)

        # 2. EL TRUCO DEFINITIVO: Le damos 150 milisegundos a Windows para que
        # termine de empaquetar y dibujar todos los campos (especialmente el calendario)
        # antes de congelar el tamaño de la ventana.
        self.after(150, lambda: self.resizable(False, False))

        self.grab_set()
        self.focus_force()
        self.bind("<Escape>", lambda _e: self.destroy())

    # ------------------------------------------------------------ #
    def _center_on(self, master):
        self.update_idletasks()

        # Obtenemos un ancho y alto estimado solo para calcular el centro matemático
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()

        mx, my = master.winfo_rootx(), master.winfo_rooty()
        mw, mh = master.winfo_width(), master.winfo_height()
        x = mx + (mw - w) // 2
        y = my + (mh - h) // 2

        # OMITIMOS forzar el tamaño. Solo le decimos "ubícate aquí (+X+Y)".
        # Esto permite que el formulario se expanda naturalmente hacia abajo.
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------------ #
    def _collect(self):
        data = {}
        for field in self._fields:
            kind, var, widget = self._widgets[field["key"]]

            if kind == "dropdown":
                value = var.get()
            elif kind == "datetime":
                date_w, time_w = widget
                date_str = date_w.get()
                time_str = time_w.get().strip()
                if not time_str:
                    time_str = "00:00"
                value = f"{date_str} {time_str}"

                # --- VALIDACIÓN DE FECHA FUTURA ---
                try:
                    dt_obj = datetime.strptime(value, "%Y-%m-%d %H:%M")
                    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                    if dt_obj > now_utc:
                        raise ValueError(
                            f"La fecha/hora no puede estar en el futuro.\nActual UTC: {now_utc.strftime('%Y-%m-%d %H:%M')}"
                        )
                except ValueError as e:
                    if "futuro" in str(e):
                        raise e
                    raise ValueError(
                        f"Formato de hora inválido en '{field['label']}'. Usa HH:MM."
                    )

            elif kind == "date":
                value = widget.get()
            else:
                value = widget.get().strip()

            if field.get("required", True) and value == "":
                raise ValueError(f"El campo '{field['label']}' es obligatorio.")

            data[field["key"]] = value

        return data

    def _submit(self):
        try:
            data = self._collect()
        except ValueError as exc:
            messagebox.showwarning("Validación", str(exc), parent=self)
            return

        ok = self._on_submit(data, self)
        if ok:
            self.destroy()
