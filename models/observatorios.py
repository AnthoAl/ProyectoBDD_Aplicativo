"""
models/observatorios.py
-----------------------
Tabla GLOBAL REPLICADA `Observatorio`.
Esquema: Id_Observatorio (PK), Nombre, Altitud, Capacidad_Resolucion
"""


def get_observatorios(db):
    sql = """
        SELECT Id_Observatorio, Nombre, Altitud, Coordenadas, Capacidad_Resolucion
        FROM Observatorio
        ORDER BY Id_Observatorio
    """
    return db.fetch_all(sql)


def insert_observatorio(db, data):
    sql = """
        INSERT INTO Observatorio
            (Id_Observatorio, Nombre, Altitud, Coordenadas, Capacidad_Resolucion)
        VALUES (?, ?, ?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Id_Observatorio"],
            data["Nombre"],
            data["Altitud"],
            data["Coordenadas"],
            data["Capacidad_Resolucion"],
        ),
    )


def update_observatorio(db, data):
    sql = """
        UPDATE Observatorio
        SET Nombre = ?, Altitud = ?, Coordenadas = ?, Capacidad_Resolucion = ?
        WHERE Id_Observatorio = ?
    """
    return db.execute(
        sql,
        (
            data["Nombre"],
            data["Altitud"],
            data["Coordenadas"],
            data["Capacidad_Resolucion"],
            data["Id_Observatorio"],
        ),
    )


def delete_observatorio(db, id_observatorio):
    return db.execute(
        "DELETE FROM Observatorio WHERE Id_Observatorio = ?", (id_observatorio,)
    )
