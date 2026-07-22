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
        "login_usuario": "operador.chile",  # <-- Credencial de acceso a la app
        "login_clave": "Chile#2026",
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
        "login_usuario": "operador.espana",  # <-- Credencial de acceso a la app
        "login_clave": "Espana#2026",
    },
}

# ---------------------------------------------------------------------------
# Linked Server configurado EN el servidor de Chile, apuntando al
# servidor de España (SQL Server Management Studio → Server Objects →
# Linked Servers). Permite referenciar tablas exclusivas de España
# (Datos_Espectral) con nombre de 4 partes desde la conexión de Chile,
# que ahora concentra todo el CRUD de Observaciones/Científicos/
# Participaciones sin importar con qué sede se inició sesión.
# ---------------------------------------------------------------------------
LINKED_SERVER_ESPANA = "DESKTOP-PB4S9LH"

# Dominios válidos para la extensión vertical del Nodo 2 (Con su significado)
TIPOS_ESPECTRALES = {
    "C": "Carbonáceo (Oscuro)",
    "S": "Silicáceo (Rocoso)",
    "M": "Metálico (Níquel-Hierro)",
    "Sq": "Transición S-Q",
    "B": "Primitivo (Rico en volátiles)",
    "Sk": "Transición S-K",
}