"""
models/observaciones.py
-----------------------
Fragmentos horizontales:
    Nodo 1 (Chile)  : Datos_Observacion_001  (SIN datos espectrales)
    Nodo 2 (España) : Datos_Observacion_002 + extensión vertical Datos_Espectral
                      [Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                       Id_Observatorio, Tipo_Espectral]

Todo el CRUD de este módulo se centraliza en el servidor de Chile
(ver ui_components/observations_view.py): sin importar con qué sede
inició sesión el operador, las consultas se ejecutan siempre contra la
conexión de Chile, y VistaGlobalObservaciones (vista particionada
global, con Linked Server hacia España) enruta cada lectura/escritura
al fragmento físico que corresponda según Id_Observatorio.

Datos_Espectral es la única tabla que NO forma parte de esa vista
particionada: es una tabla física exclusiva del servidor de España.
Por eso se referencia con nombre de 4 partes vía el Linked Server
(config.LINKED_SERVER_ESPANA) cuando se consulta desde Chile, o con su
nombre local cuando la conexión activa ya es España.

Clave primaria compuesta asumida:
    (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio)
"""

from config import LINKED_SERVER_ESPANA, NODES

DATE_FMT_HINT = "YYYY-MM-DD HH:MM"


# --------------------------------------------------------------------- #
# Datos_Espectral: referencia calificada según desde dónde se consulte
# --------------------------------------------------------------------- #
def _espectral_ref(db):
    if db.sede == "chile":
        espana = NODES["espana"]
        return f"[{LINKED_SERVER_ESPANA}].[{espana['database']}].dbo.Datos_Espectral"
    return "Datos_Espectral"


def _espectral_join(db):
    ref = _espectral_ref(db)
    join = f"""
        LEFT JOIN {ref} E
               ON E.Cod_Cientifico  = O.Cod_Cientifico
              AND E.Id_Asteroide    = O.Id_Asteroide
              AND E.Fecha_Hora      = O.Fecha_Hora
              AND E.Id_Observatorio = O.Id_Observatorio
    """
    return "E.Tipo_Espectral", join


# --------------------------------------------------------------------- #
# READ
# --------------------------------------------------------------------- #
def get_observaciones(db, filtro="ambas"):
    """
    filtro:
        "chile"  -> solo Nodo 1 · Chile   (WHERE Id_Observatorio = 1)
        "espana" -> solo Nodo 2 · España  (WHERE Id_Observatorio = 2)
        "ambas"  -> ambos nodos, sin filtro (federados por la vista global)
    """
    if filtro == "chile":
        where_clause = "WHERE O.Id_Observatorio = 1"
    elif filtro == "espana":
        where_clause = "WHERE O.Id_Observatorio = 2"
    elif filtro == "ambas":
        where_clause = ""
    else:
        raise ValueError(f"Filtro de sede no soportado: {filtro!r}")

    tipo_col, join_espectral = _espectral_join(db)

    sql = f"""
        SELECT O.Cod_Cientifico,
               O.Id_Asteroide,
               C.Primer_Nombre + ' ' + C.Primer_Apellido AS Cientifico,
               A.Nombre  AS Asteroide,
               O.Fecha_Hora,
               O.Id_Observatorio,
               O.Magnitud_Aparente,
               O.Distancia_Relativa,
               O.Velocidad_Aproximada AS Velocidad, -- Alias para la UI
               {tipo_col} AS Tipo_Espectral
        FROM VistaGlobalObservaciones O
        LEFT JOIN VistaGlobalCientificos C
               ON C.Cod_Cientifico = O.Cod_Cientifico
              AND C.Id_Observatorio = O.Id_Observatorio
        LEFT JOIN Asteroide A ON A.Id_Asteroide = O.Id_Asteroide
        {join_espectral}
        {where_clause}
        ORDER BY O.Fecha_Hora DESC
    """
    return db.fetch_all(sql)


# --------------------------------------------------------------------- #
# CREATE
# --------------------------------------------------------------------- #
def insert_observacion(db, data):
    """data debe incluir "Id_Observatorio" (1 · Chile o 2 · España),
    la sede real del registro — independiente de la conexión usada."""
    base_sql = """
        INSERT INTO VistaGlobalObservaciones
            (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio,
             Magnitud_Aparente, Distancia_Relativa, Velocidad_Aproximada)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    id_obs = data["Id_Observatorio"]
    base_params = (
        data["Cod_Cientifico"],
        data["Id_Asteroide"],
        data["Fecha_Hora"],
        id_obs,
        data["Magnitud_Aparente"],
        data["Distancia_Relativa"],
        data["Velocidad"],
    )

    tipo = data.get("Tipo_Espectral")
    if id_obs == 2 and tipo:
        # Atomicidad: registro base + extensión vertical Datos_Espectral.
        statements = [
            (base_sql, base_params),
            (
                f"""
                INSERT INTO {_espectral_ref(db)}
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                (data["Cod_Cientifico"], data["Id_Asteroide"], data["Fecha_Hora"], tipo),
            ),
        ]
        return db.execute_transaction(statements)

    return db.execute(base_sql, base_params)


# --------------------------------------------------------------------- #
# UPDATE
# --------------------------------------------------------------------- #
def update_observacion(db, pk, data):
    """pk debe incluir "Id_Observatorio" (la sede real de la fila editada)."""
    base_sql = """
        UPDATE VistaGlobalObservaciones
        SET Magnitud_Aparente = ?, Distancia_Relativa = ?, Velocidad_Aproximada = ?
        WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
    """
    base_params = (
        data["Magnitud_Aparente"],
        data["Distancia_Relativa"],
        data["Velocidad"],
        pk["Cod_Cientifico"],
        pk["Id_Asteroide"],
        pk["Fecha_Hora"],
    )

    if pk["Id_Observatorio"] != 2:
        return db.execute(base_sql, base_params)

    # España: sincronizamos la extensión vertical (borrar e insertar de nuevo).
    statements = [
        (base_sql, base_params),
        (
            f"""
            DELETE FROM {_espectral_ref(db)}
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
            """,
            (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
        ),
    ]

    tipo = data.get("Tipo_Espectral")
    if tipo:
        statements.append(
            (
                f"""
                INSERT INTO {_espectral_ref(db)}
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"], tipo),
            )
        )

    return db.execute_transaction(statements)


# --------------------------------------------------------------------- #
# DELETE
# --------------------------------------------------------------------- #
def delete_observacion(db, pk):
    """pk debe incluir "Id_Observatorio" (la sede real de la fila borrada)."""
    base_sql = """
        DELETE FROM VistaGlobalObservaciones
        WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
    """
    base_params = (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"])

    if pk["Id_Observatorio"] != 2:
        return db.execute(base_sql, base_params)

    # Primero borramos la dependencia (Datos_Espectral) por integridad referencial.
    statements = [
        (
            f"""
            DELETE FROM {_espectral_ref(db)}
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
            """,
            (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
        ),
        (base_sql, base_params),
    ]
    return db.execute_transaction(statements)