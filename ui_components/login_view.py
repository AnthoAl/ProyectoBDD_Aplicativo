"""
ui_components/login_view.py
---------------------------
Pantalla de Login. El usuario elige la SEDE (nodo) de ingreso:

    self.sede = "chile"  -> Nodo 1 · Paranal      (Id_Observatorio = 1)
    self.sede = "espana" -> Nodo 2 · Roque         (Id_Observatorio = 2)

Desde aquí se bifurca todo el comportamiento de la aplicación.
"""

from tkinter import messagebox

import customtkinter as ctk

import theme
from config import NODES
from db_connection import DBConnection, DBError


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login):
        super().__init__(master, fg_color=theme.BG_MAIN)
        self.on_login = on_login
        self.sede_var = ctk.StringVar(value="chile")

        card = ctk.CTkFrame(
            self, fg_color=theme.BG_PANEL, corner_radius=16,
            border_width=1, border_color=theme.BORDER, width=460,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=40, pady=36)

        ctk.CTkLabel(inner, text="◈ NASA / PDCO",
                     font=theme.mono_font(22, "bold"),
                     text_color=theme.ACCENT).pack(anchor="w")
        ctk.CTkLabel(inner,
                     text="PLANETARY DEFENSE — ASTEROID MONITORING\n"
                          "DISTRIBUTED DATABASE ACCESS TERMINAL",
                     font=theme.mono_font(10), justify="left",
                     text_color=theme.TEXT_SEC).pack(anchor="w",
                                                     pady=(4, 22))

        # ---------------- Usuario ----------------
        ctk.CTkLabel(inner, text="OPERADOR",
                     font=theme.mono_font(10, "bold"),
                     text_color=theme.TEXT_SEC).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(
            inner, width=360, height=38, fg_color=theme.BG_MAIN,
            border_color=theme.BORDER, border_width=1,
            text_color=theme.TEXT_MAIN, font=theme.ui_font(13),
            placeholder_text="usuario.nasa",
        )
        self.entry_user.pack(pady=(4, 18))

        # ---------------- Selección de sede ----------------
        ctk.CTkLabel(inner, text="SEDE DE INGRESO (NODO)",
                     font=theme.mono_font(10, "bold"),
                     text_color=theme.TEXT_SEC).pack(anchor="w",
                                                     pady=(0, 6))

        self._node_frames = {}
        for sede in ("chile", "espana"):
            frame = self._node_option(inner, sede)
            frame.pack(fill="x", pady=4)
            self._node_frames[sede] = frame
        self._refresh_selection()

        # ---------------- Conectar ----------------
        ctk.CTkButton(
            inner, text="⇥ CONECTAR AL NODO", height=42, width=360,
            corner_radius=8, fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOV, text_color=theme.BG_MAIN,
            font=theme.mono_font(13, "bold"), command=self._connect,
        ).pack(pady=(22, 0))

    # ------------------------------------------------------------ #
    def _node_option(self, parent, sede):
        cfg = NODES[sede]
        frame = ctk.CTkFrame(parent, fg_color=theme.BG_MAIN,
                             corner_radius=10, border_width=1,
                             border_color=theme.BORDER, cursor="hand2")

        title = ctk.CTkLabel(frame, text=cfg["label"],
                             font=theme.mono_font(12, "bold"),
                             text_color=theme.TEXT_MAIN)
        title.pack(anchor="w", padx=14, pady=(10, 0))

        if sede == "chile":
            detail = "Fragmentos: Cientifico_001 · Datos_Observacion_001"
        else:
            detail = ("Fragmentos: Cientifico_002 · Datos_Observacion_002 "
                      "+ Datos_Espectral")
        sub = ctk.CTkLabel(frame, text=detail, font=theme.ui_font(10),
                           text_color=theme.TEXT_SEC)
        sub.pack(anchor="w", padx=14, pady=(0, 10))

        def select(_e=None, s=sede):
            self.sede_var.set(s)
            self._refresh_selection()

        for widget in (frame, title, sub):
            widget.bind("<Button-1>", select)
        return frame

    def _refresh_selection(self):
        selected = self.sede_var.get()
        for sede, frame in self._node_frames.items():
            if sede == selected:
                frame.configure(border_color=theme.ACCENT,
                                fg_color=theme.ACCENT_DIM)
            else:
                frame.configure(border_color=theme.BORDER,
                                fg_color=theme.BG_MAIN)

    # ------------------------------------------------------------ #
    def _connect(self):
        usuario = self.entry_user.get().strip()
        if usuario == "":
            usuario = "operador"

        sede = self.sede_var.get()
        try:
            db = DBConnection(sede)
            db.test_connection()
        except DBError as exc:
            messagebox.showerror("Conexión fallida", str(exc),
                                 parent=self.winfo_toplevel())
            return

        self.on_login(sede, usuario, db)
