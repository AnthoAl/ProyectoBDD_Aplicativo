"""
ui_components/topbar.py
-----------------------
Barra superior: título de la vista actual, sede conectada y reloj UTC.
"""

from datetime import datetime, timezone

import customtkinter as ctk

import theme


class Topbar(ctk.CTkFrame):
    def __init__(self, master, sede_cfg, usuario):
        super().__init__(master, height=64, corner_radius=0,
                         fg_color=theme.BG_MAIN)
        self.pack_propagate(False)

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", padx=26)

        self.lbl_title = ctk.CTkLabel(
            left, text="OBSERVACIONES", font=theme.mono_font(18, "bold"),
            text_color=theme.TEXT_MAIN,
        )
        self.lbl_title.pack(anchor="w", pady=(12, 0))

        self.lbl_sub = ctk.CTkLabel(
            left, text=sede_cfg["label"], font=theme.ui_font(11),
            text_color=theme.TEXT_SEC,
        )
        self.lbl_sub.pack(anchor="w")

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=26)

        self.lbl_clock = ctk.CTkLabel(
            right, text="", font=theme.mono_font(13),
            text_color=theme.ACCENT,
        )
        self.lbl_clock.pack(anchor="e", pady=(12, 0))

        ctk.CTkLabel(
            right, text=f"OPERADOR: {usuario.upper()}",
            font=theme.mono_font(10), text_color=theme.TEXT_SEC,
        ).pack(anchor="e")

        self._tick()

    def set_title(self, text):
        self.lbl_title.configure(text=text.upper())

    def _tick(self):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.lbl_clock.configure(text=now)
        self.after(1000, self._tick)
