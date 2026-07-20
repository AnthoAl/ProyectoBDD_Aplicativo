"""
ui_components/login_view.py
---------------------------
Pantalla de Login única para ambas sedes. El usuario ingresa su
usuario y contraseña; estas credenciales están quemadas en `config.py`
(una pareja usuario/clave por nodo) y determinan automáticamente a qué
sede se conecta:

    login_usuario/login_clave de NODES["chile"]  -> Nodo 1 · Paranal   (Id_Observatorio = 1)
    login_usuario/login_clave de NODES["espana"] -> Nodo 2 · Roque     (Id_Observatorio = 2)

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
        ctk.CTkLabel(inner, text="USUARIO",
                     font=theme.mono_font(10, "bold"),
                     text_color=theme.TEXT_SEC).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(
            inner, width=360, height=38, fg_color=theme.BG_MAIN,
            border_color=theme.BORDER, border_width=1,
            text_color=theme.TEXT_MAIN, font=theme.ui_font(13),
            placeholder_text="usuario.nasa",
        )
        self.entry_user.pack(pady=(4, 18))

        # ---------------- Contraseña ----------------
        ctk.CTkLabel(inner, text="CONTRASEÑA",
                     font=theme.mono_font(10, "bold"),
                     text_color=theme.TEXT_SEC).pack(anchor="w")
        self.entry_pass = ctk.CTkEntry(
            inner, width=360, height=38, fg_color=theme.BG_MAIN,
            border_color=theme.BORDER, border_width=1,
            text_color=theme.TEXT_MAIN, font=theme.ui_font(13),
            placeholder_text="••••••••", show="•",
        )
        self.entry_pass.pack(pady=(4, 0))
        self.entry_pass.bind("<Return>", lambda _e: self._connect())

        # ---------------- Ingresar ----------------
        ctk.CTkButton(
            inner, text="⇥ INGRESAR AL SISTEMA", height=42, width=360,
            corner_radius=8, fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOV, text_color=theme.BG_MAIN,
            font=theme.mono_font(13, "bold"), command=self._connect,
        ).pack(pady=(22, 0))

    # ------------------------------------------------------------ #
    @staticmethod
    def _resolver_sede(usuario, clave):
        """Determina la sede según las credenciales quemadas en NODES."""
        for sede, cfg in NODES.items():
            if usuario == cfg["login_usuario"] and clave == cfg["login_clave"]:
                return sede
        return None

    # ------------------------------------------------------------ #
    def _connect(self):
        usuario = self.entry_user.get().strip()
        clave = self.entry_pass.get()

        sede = self._resolver_sede(usuario, clave)
        if sede is None:
            messagebox.showerror(
                "Credenciales inválidas",
                "Usuario o contraseña incorrectos.",
                parent=self.winfo_toplevel(),
            )
            return

        try:
            db = DBConnection(sede)
            db.test_connection()
        except DBError as exc:
            messagebox.showerror("Conexión fallida", str(exc),
                                 parent=self.winfo_toplevel())
            return

        self.on_login(sede, usuario, db)