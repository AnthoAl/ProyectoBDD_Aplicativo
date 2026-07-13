"""
models/asteroides.py
--------------------
Tabla GLOBAL REPLICADA `Asteroide` (idéntica en ambos nodos).
Esquema: Id_Asteroide (PK), Nombre, Designación, Diametro_Estimado, Es_Peligroso
"""


def get_asteroides(db):
    sql = """
        SELECT Id_Asteroide, Nombre, Designacion_Provisional,
               Diametro_Estimado, Es_Peligroso
        FROM Asteroide
        ORDER BY Id_Asteroide
    """
    return db.fetch_all(sql)


def insert_asteroide(db, data):
    sql = """
        INSERT INTO Asteroide
            (Id_Asteroide, Nombre, Designacion_Provisional, Diametro_Estimado, Es_Peligroso)
        VALUES (?, ?, ?, ?, ?)
    """
    return db.execute(
        sql,
        (
            data["Id_Asteroide"],
            data["Nombre"],
            data["Designacion_Provisional"],
            data["Diametro_Estimado"],
            data["Es_Peligroso"],
        ),
    )


def update_asteroide(db, data):
    sql = """
        UPDATE Asteroide
        SET Nombre = ?, Designacion_Provisional = ?, Diametro_Estimado = ?, Es_Peligroso = ?
        WHERE Id_Asteroide = ?
    """
    return db.execute(
        sql,
        (
            data["Nombre"],
            data["Designacion_Provisional"],
            data["Diametro_Estimado"],
            data["Es_Peligroso"],
            data["Id_Asteroide"],
        ),
    )


def delete_asteroide(db, id_asteroide):
    return db.execute("DELETE FROM Asteroide WHERE Id_Asteroide = ?", (id_asteroide,))
