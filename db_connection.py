"""
db_connection.py
----------------
Capa de acceso a datos vía pyodbc.

Expone una clase `DBConnection` ligada a una sede ("chile" | "espana")
con funciones genéricas:

    fetch_all(sql, params)            -> SELECT, retorna lista de dicts
    execute(sql, params)              -> INSERT / UPDATE / DELETE (autocommit)
    execute_transaction(statements)   -> Varias sentencias atómicas (commit/rollback)

NOTA: Sin `match-case`. Todo el ruteo se resuelve con if/elif/else
para asegurar compatibilidad con el entorno local.
"""

import pyodbc

from config import NODES


class DBError(Exception):
    """Error de capa de datos, con mensaje apto para mostrar en UI."""


class DBConnection:
    def __init__(self, sede):
        # --- Ruteo de nodo (if/elif/else, prohibido match-case) -----------
        if sede == "chile":
            self.cfg = NODES["chile"]
        elif sede == "espana":
            self.cfg = NODES["espana"]
        else:
            raise DBError(f"Sede desconocida: {sede!r}")

        self.sede = sede
        self._conn_str = self._build_conn_str(self.cfg)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _build_conn_str(cfg):
        base = (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
        )
        if cfg.get("trusted"):
            base += "Trusted_Connection=yes;"
        else:
            base += f"UID={cfg['uid']};PWD={cfg['pwd']};"
        return base

    def get_connection(self):
        try:
            return pyodbc.connect(self._conn_str, timeout=5)
        except pyodbc.Error as exc:
            raise DBError(
                f"No fue posible conectar al nodo " f"{self.cfg['short']}:\n{exc}"
            ) from exc

    def test_connection(self):
        """Prueba rápida de conectividad (usada por la pantalla de Login)."""
        conn = self.get_connection()
        conn.close()
        return True

    # ------------------------------------------------------------------ #
    # SELECT genérico
    # ------------------------------------------------------------------ #
    def fetch_all(self, sql, params=()):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            return rows
        except pyodbc.Error as exc:
            raise DBError(f"Error en SELECT:\n{exc}") from exc
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    # INSERT / UPDATE / DELETE genérico (una sentencia)
    # ------------------------------------------------------------------ #
    def execute(self, sql, params=()):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            # 1. Habilitar XACT_ABORT para transacciones distribuidas en esta sesión
            cur.execute("SET XACT_ABORT ON;")

            cur.execute(sql, params)
            affected = cur.rowcount
            conn.commit()
            return affected
        except pyodbc.Error as exc:
            conn.rollback()
            raise DBError(f"Error al ejecutar la sentencia:\n{exc}") from exc
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    # Transacción atómica: lista de (sql, params)
    # Usada en el Nodo España para insertar en Datos_Observacion_002
    # y su extensión vertical Datos_Espectral en una sola unidad lógica.
    # ------------------------------------------------------------------ #
    def execute_transaction(self, statements):
        conn = self.get_connection()
        try:
            conn.autocommit = False
            cur = conn.cursor()

            # 1. Habilitar XACT_ABORT para la transacción distribuida
            cur.execute("SET XACT_ABORT ON;")

            total = 0
            for sql, params in statements:
                cur.execute(sql, params)
                total += cur.rowcount
            conn.commit()
            return total
        except pyodbc.Error as exc:
            conn.rollback()
            raise DBError(f"Transacción revertida (rollback):\n{exc}") from exc
        finally:
            conn.close()
