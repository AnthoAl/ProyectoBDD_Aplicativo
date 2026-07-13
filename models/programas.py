"""
models/programas.py
-------------------
Tabla GLOBAL REPLICADA `Programa`.
Esquema: Id_Programa (PK), Nombre_Mision, Presupuesto, Estado
"""


def get_programas(db):
    sql = """
        SELECT Id_Programa, Nombre_Mision, Presupuesto_asignado, Estado
        FROM Programa
        ORDER BY Id_Programa
    """
    return db.fetch_all(sql)


def insert_programa(db, data):
    sql = """
        INSERT INTO Programa (Id_Programa, Nombre_Mision, Presupuesto_asignado, Estado)
        VALUES (?, ?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Id_Programa"],
            data["Nombre_Mision"],
            data["Presupuesto_asignado"],
            data["Estado"],
        ),
    )


def update_programa(db, data):
    sql = """
        UPDATE Programa
        SET Nombre_Mision = ?, Presupuesto_asignado = ?, Estado = ?
        WHERE Id_Programa = ?
    """
    return db.execute(
        sql,
        (
            data["Nombre_Mision"],
            data["Presupuesto_asignado"],
            data["Estado"],
            data["Id_Programa"],
        ),
    )


def delete_programa(db, id_programa):
    return db.execute("DELETE FROM Programa WHERE Id_Programa = ?", (id_programa,))
