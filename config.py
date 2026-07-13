"""
config.py
---------
Configuración de los nodos de la Base de Datos Distribuida (BDD).

Ajusta aquí los servidores, instancias y credenciales de cada sede.
La fragmentación horizontal primaria se controla con `id_observatorio`.
"""

APP_NAME = "NASA · PDCO — Planetary Defense Distributed Database"

# ---------------------------------------------------------------------------
# Definición de nodos.
#   driver     : Driver ODBC instalado en la máquina cliente.
#   server     : Instancia de SQL Server del nodo.
#   database   : Base de datos local del nodo.
#   trusted    : True -> Autenticación de Windows. False -> usuario/clave SQL.
# ---------------------------------------------------------------------------
NODES = {
    "chile": {
        "label": "NODO 1 · CHILE — Observatorio Paranal",
        "short": "CHILE · PARANAL",
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "ANTHO-A25",  # <-- Ajustar
        "database": "ObservatorioChile",  # <-- Ajustar
        "uid": "sa",
        "pwd": "P@ssw0rd",
        "id_observatorio": 1,  # Condición de fragmentación
        "tabla_cientifico": "Cientifico_001",
        "tabla_participacion": "Participacion_001",
        "tabla_observacion": "Datos_Observacion_001",
        "tiene_espectral": False,
    },
    "espana": {
        "label": "NODO 2 · ESPAÑA — Roque de los Muchachos",
        "short": "ESPAÑA · ROQUE",
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "DESKTOP-PB4S9LH",  # <-- Ajustar
        "database": "ObservatorioEspaña",  # <-- Ajustar
        "uid": "sa",
        "pwd": "Ni123456",
        "id_observatorio": 2,  # Condición de fragmentación
        "tabla_cientifico": "Cientifico_002",
        "tabla_participacion": "Participacion_002",
        "tabla_observacion": "Datos_Observacion_002",
        "tiene_espectral": True,  # Extensión vertical Datos_Espectral
    },
}

# Dominios válidos para la extensión vertical del Nodo 2
TIPOS_ESPECTRALES = ["C", "S", "M", "Sq", "B", "Sk"]
