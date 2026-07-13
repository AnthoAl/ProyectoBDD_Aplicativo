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
def get_cientificos(db):
    """Lectura vía vista particionada global, filtrada por el nodo local."""
    sql = """
        SELECT Cod_Cientifico, Primer_Nombre, Primer_Apellido, Especialidad, Nacionalidad, Id_Observatorio
        FROM VistaGlobalCientificos
        ORDER BY Id_Observatorio, Cod_Cientifico
    """
    # return db.fetch_all(sql, (db.cfg["id_observatorio"],))


def get_cientificos_global(db):
    """Lectura de TODOS los científicos de la federación (ambos nodos)."""
    sql = """
        SELECT Cod_Cientifico, Primer_Nombre, Primer_Apellido, Especialidad, Nacionalidad, Id_Observatorio
        FROM VistaGlobalCientificos
        ORDER BY Id_Observatorio, Cod_Cientifico
    """
    return db.fetch_all(sql)


def insert_cientifico(db, data):
    tabla = db.cfg["tabla_cientifico"]  # Cientifico_001 | Cientifico_002
    sql = f"""
        INSERT INTO {tabla}
            (Cod_Cientifico, Nombre, Especialidad, Id_Observatorio)
        VALUES (?, ?, ?, ?)
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
    tabla = db.cfg["tabla_cientifico"]
    sql = f"""
        UPDATE {tabla}
        SET Primer_Nombre = ?, Primer_Apellido = ?, Especialidad = ?, Nacionalidad = ?
        WHERE Cod_Cientifico = ? AND Id_Observatorio = ?
    """
    return db.execute(
        sql,
        (
            data["Primer_Nombre"],
            data["Primer_Apellido"],
            data["Especialidad"],
            data["Nacionalidad"],
            data["Cod_Cientifico"],
            db.cfg["id_observatorio"],
        ),
    )


def delete_cientifico(db, cod_cientifico):
    tabla = db.cfg["tabla_cientifico"]
    sql = f"DELETE FROM {tabla} WHERE Cod_Cientifico = ? AND Id_Observatorio = ?"
    return db.execute(sql, (cod_cientifico, db.cfg["id_observatorio"]))


# --------------------------------------------------------------------- #
# PARTICIPACIONES
# --------------------------------------------------------------------- #
def get_participaciones(db):
    sql = """
        SELECT P.Cod_Cientifico, P.Id_Programa, P.Id_Observatorio,
               C.Nombre     AS Cientifico,
               PR.Nombre_Mision
        FROM VistaGlobalParticipaciones P
        LEFT JOIN VistaGlobalCientificos C
               ON C.Cod_Cientifico = P.Cod_Cientifico
              AND C.Id_Observatorio = P.Id_Observatorio
        LEFT JOIN Programa PR ON PR.Id_Programa = P.Id_Programa
        WHERE P.Id_Observatorio = ?
        ORDER BY P.Cod_Cientifico, P.Id_Programa
    """
    return db.fetch_all(sql, (db.cfg["id_observatorio"],))


def insert_participacion(db, data):
    tabla = db.cfg["tabla_participacion"]
    sql = f"""
        INSERT INTO {tabla} (Cod_Cientifico, Id_Programa, Id_Observatorio)
        VALUES (?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Cod_Cientifico"],
            data["Id_Programa"],
            db.cfg["id_observatorio"],
        ),
    )


def delete_participacion(db, cod_cientifico, id_programa):
    tabla = db.cfg["tabla_participacion"]
    sql = (
        f"DELETE FROM {tabla} "
        f"WHERE Cod_Cientifico = ? AND Id_Programa = ? AND Id_Observatorio = ?"
    )
    return db.execute(sql, (cod_cientifico, id_programa, db.cfg["id_observatorio"]))
