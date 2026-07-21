"""
models/cientificos.py
---------------------
Tablas FRAGMENTADAS por sede:
    Nodo 1 (Chile)  : Cientifico_001 / Participacion_001
    Nodo 2 (España) : Cientifico_002 / Participacion_002

Vistas particionadas globales (transparencia de fragmentación):
    VistaGlobalCientificos, VistaGlobalParticipaciones

Las escrituras (INSERT/UPDATE/DELETE) van SIEMPRE al fragmento local
del nodo. Las lecturas usan la vista global filtrando por la condición
de fragmentación horizontal primaria (Id_Observatorio).

NOTA: Si tu esquema real de Cientifico difiere, ajusta las columnas
solo en este archivo (la UI las toma desde aquí).
"""


# --------------------------------------------------------------------- #
# CIENTÍFICOS
# --------------------------------------------------------------------- #
def get_cientificos(db, filtro="propio"):
    """
    Lectura vía vista particionada global.

    filtro:
        "chile"  -> solo Nodo 1 · Chile   (Id_Observatorio = 1)
        "espana" -> solo Nodo 2 · España  (Id_Observatorio = 2)
        "ambas"  -> ambos nodos, sin filtro (federados por la vista global)
        "propio" -> el nodo local conectado (usado internamente por los
                    dropdowns de otras vistas, que solo pueden referenciar
                    científicos de su propio nodo al escribir)
    """
    if filtro == "chile":
        where_clause, params = "WHERE Id_Observatorio = 1", ()
    elif filtro == "espana":
        where_clause, params = "WHERE Id_Observatorio = 2", ()
    elif filtro == "ambas":
        where_clause, params = "", ()
    elif filtro == "propio":
        where_clause, params = "WHERE Id_Observatorio = ?", (db.cfg["id_observatorio"],)
    else:
        raise ValueError(f"Filtro de sede no soportado: {filtro!r}")

    sql = f"""
        SELECT Cod_Cientifico, Primer_Nombre, Primer_Apellido, Especialidad, Nacionalidad, Id_Observatorio
        FROM VistaGlobalCientificos
        {where_clause}
        ORDER BY Id_Observatorio, Cod_Cientifico
    """
    return db.fetch_all(sql, params)


def insert_cientifico(db, data):
    sql = """
        INSERT INTO VistaGlobalCientificos
            (Cod_Cientifico, Primer_Nombre, Primer_Apellido, Especialidad, Nacionalidad, Id_Observatorio)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Cod_Cientifico"],
            data["Primer_Nombre"],
            data["Primer_Apellido"],
            data["Especialidad"],
            data["Nacionalidad"],
            db.cfg["id_observatorio"],
        ),
    )


def update_cientifico(db, data):
    sql = """
        UPDATE VistaGlobalCientificos
        SET Primer_Nombre = ?, Primer_Apellido = ?, Especialidad = ?, Nacionalidad = ?
        WHERE Cod_Cientifico = ?
    """
    return db.execute(
        sql,
        (
            data["Primer_Nombre"],
            data["Primer_Apellido"],
            data["Especialidad"],
            data["Nacionalidad"],
            data["Cod_Cientifico"],
        ),
    )


def delete_cientifico(db, cod_cientifico):
    sql = """
        DELETE FROM VistaGlobalCientificos 
        WHERE Cod_Cientifico = ?
    """
    return db.execute(sql, (cod_cientifico,))


# --------------------------------------------------------------------- #
# PARTICIPACIONES
# --------------------------------------------------------------------- #
def get_participaciones(db, filtro="propio"):
    """
    Lectura vía vista particionada global.

    filtro: "chile" | "espana" | "ambas" | "propio" (ver get_cientificos).
    """
    if filtro == "chile":
        where_clause, params = "WHERE P.Id_Observatorio = 1", ()
    elif filtro == "espana":
        where_clause, params = "WHERE P.Id_Observatorio = 2", ()
    elif filtro == "ambas":
        where_clause, params = "", ()
    elif filtro == "propio":
        where_clause, params = "WHERE P.Id_Observatorio = ?", (db.cfg["id_observatorio"],)
    else:
        raise ValueError(f"Filtro de sede no soportado: {filtro!r}")

    sql = f"""
        SELECT P.Cod_Cientifico, P.Id_Programa, P.Fecha_Inicio, P.Id_Observatorio,
               P.Rol_En_Mision,  -- <-- COLUMNA AGREGADA PARA EVITAR EL KEYERROR
               P.Fecha_Fin,      -- <-- Agregada por si también la incluyes en la UI
               C.Primer_Nombre + ' ' + C.Primer_Apellido AS Cientifico,
               PR.Nombre_Mision
        FROM VistaGlobalParticipaciones P
        LEFT JOIN VistaGlobalCientificos C
               ON C.Cod_Cientifico = P.Cod_Cientifico
              AND C.Id_Observatorio = P.Id_Observatorio
        LEFT JOIN Programa PR ON PR.Id_Programa = P.Id_Programa
        {where_clause}
        ORDER BY P.Id_Observatorio, P.Cod_Cientifico, P.Id_Programa, P.Fecha_Inicio
    """
    return db.fetch_all(sql, params)


def insert_participacion(db, data):
    sql = """
        INSERT INTO VistaGlobalParticipaciones (Cod_Cientifico, Id_Programa, Fecha_Inicio, Id_Observatorio, Fecha_Fin, Rol_En_Mision)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Cod_Cientifico"],
            data["Id_Programa"],
            data["Fecha_Inicio"],
            db.cfg["id_observatorio"],
            data["Fecha_Fin"],
            data["Rol_En_Mision"],
        ),
    )


def update_participacion(db, pk, data):
    """
    Actualiza exclusivamente los campos no primarios.
    Se envía a VistaGlobalParticipaciones para mantener la transparencia
    de fragmentación.
    """
    sql = """
        UPDATE VistaGlobalParticipaciones
        SET Fecha_Fin = ?, Rol_En_Mision = ?
        WHERE Cod_Cientifico = ? AND Id_Programa = ? AND Fecha_Inicio = ?
    """
    return db.execute(
        sql,
        (
            data["Fecha_Fin"],
            data["Rol_En_Mision"],
            pk["Cod_Cientifico"],
            pk["Id_Programa"],
            pk["Fecha_Inicio"],
        ),
    )


def delete_participacion(db, cod_cientifico, id_programa, fecha_inicio):
    sql = """
        DELETE FROM VistaGlobalParticipaciones 
        WHERE Cod_Cientifico = ? AND Id_Programa = ? AND Fecha_Inicio = ?
    """
    return db.execute(sql, (cod_cientifico, id_programa, fecha_inicio))