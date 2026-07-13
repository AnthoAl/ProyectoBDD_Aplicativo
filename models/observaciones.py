"""
models/observaciones.py
-----------------------
Fragmentos horizontales:
    Nodo 1 (Chile)  : Datos_Observacion_001  (SIN datos espectrales)
    Nodo 2 (España) : Datos_Observacion_002 + extensión vertical Datos_Espectral
                      [Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                       Id_Observatorio, Tipo_Espectral]

Lecturas:
    - VistaGlobalObservaciones filtrada por la condición de fragmentación
      horizontal primaria: WHERE Id_Observatorio = 1 (Chile) o = 2 (España).
    - España añade LEFT JOIN a Datos_Espectral (fragmentación vertical).

Escrituras:
    - Chile  : INSERT/UPDATE/DELETE directo sobre Datos_Observacion_001.
    - España : Transacción ATÓMICA sobre Datos_Observacion_002 y, si aplica,
               Datos_Espectral (commit conjunto, rollback conjunto).

Clave primaria compuesta asumida:
    (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio)
"""

DATE_FMT_HINT = "YYYY-MM-DD HH:MM"


# --------------------------------------------------------------------- #
# READ
# --------------------------------------------------------------------- #
def get_observaciones(db):
    if db.sede == "chile":
        # Nodo 1 — columnas básicas, sin dominio espectral.
        sql = """
            SELECT O.Cod_Cientifico,
                   O.Id_Asteroide,
                   C.Nombre  AS Cientifico,
                   A.Nombre  AS Asteroide,
                   O.Fecha_Hora,
                   O.Magnitud_Aparente,
                   O.Distancia_Relativa,
                   O.Velocidad
            FROM VistaGlobalObservaciones O
            LEFT JOIN VistaGlobalCientificos C
                   ON C.Cod_Cientifico = O.Cod_Cientifico
                  AND C.Id_Observatorio = O.Id_Observatorio
            LEFT JOIN Asteroide A ON A.Id_Asteroide = O.Id_Asteroide
            WHERE O.Id_Observatorio = 1
            ORDER BY O.Fecha_Hora DESC
        """
        return db.fetch_all(sql)

    elif db.sede == "espana":
        # Nodo 2 — se anexa la extensión vertical Datos_Espectral.
        sql = """
            SELECT O.Cod_Cientifico,
                   O.Id_Asteroide,
                   C.Nombre  AS Cientifico,
                   A.Nombre  AS Asteroide,
                   O.Fecha_Hora,
                   O.Magnitud_Aparente,
                   O.Distancia_Relativa,
                   O.Velocidad,
                   E.Tipo_Espectral
            FROM VistaGlobalObservaciones O
            LEFT JOIN VistaGlobalCientificos C
                   ON C.Cod_Cientifico = O.Cod_Cientifico
                  AND C.Id_Observatorio = O.Id_Observatorio
            LEFT JOIN Asteroide A ON A.Id_Asteroide = O.Id_Asteroide
            LEFT JOIN Datos_Espectral E
                   ON E.Cod_Cientifico  = O.Cod_Cientifico
                  AND E.Id_Asteroide    = O.Id_Asteroide
                  AND E.Fecha_Hora      = O.Fecha_Hora
                  AND E.Id_Observatorio = O.Id_Observatorio
            WHERE O.Id_Observatorio = 2
            ORDER BY O.Fecha_Hora DESC
        """
        return db.fetch_all(sql)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")


# --------------------------------------------------------------------- #
# CREATE
# --------------------------------------------------------------------- #
def insert_observacion(db, data):
    """
    data = {Cod_Cientifico, Id_Asteroide, Fecha_Hora,
            Magnitud_Aparente, Distancia_Relativa, Velocidad,
            Tipo_Espectral (opcional, solo España)}
    """
    if db.sede == "chile":
        sql = """
            INSERT INTO Datos_Observacion_001
                (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio,
                 Magnitud_Aparente, Distancia_Relativa, Velocidad)
            VALUES (?, ?, ?, 1, ?, ?, ?)
        """
        return db.execute(sql, (
            data["Cod_Cientifico"], data["Id_Asteroide"], data["Fecha_Hora"],
            data["Magnitud_Aparente"], data["Distancia_Relativa"],
            data["Velocidad"],
        ))

    elif db.sede == "espana":
        # Atomicidad: observación + (opcional) tipo espectral en UNA transacción.
        statements = [(
            """
            INSERT INTO Datos_Observacion_002
                (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio,
                 Magnitud_Aparente, Distancia_Relativa, Velocidad)
            VALUES (?, ?, ?, 2, ?, ?, ?)
            """,
            (data["Cod_Cientifico"], data["Id_Asteroide"], data["Fecha_Hora"],
             data["Magnitud_Aparente"], data["Distancia_Relativa"],
             data["Velocidad"]),
        )]

        tipo = data.get("Tipo_Espectral")
        if tipo:
            statements.append((
                """
                INSERT INTO Datos_Espectral
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                     Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                (data["Cod_Cientifico"], data["Id_Asteroide"],
                 data["Fecha_Hora"], tipo),
            ))

        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")


# --------------------------------------------------------------------- #
# UPDATE
# --------------------------------------------------------------------- #
def update_observacion(db, pk, data):
    """
    pk   = {Cod_Cientifico, Id_Asteroide, Fecha_Hora}  (clave original)
    data = valores nuevos de medición (+ Tipo_Espectral en España).
    """
    if db.sede == "chile":
        sql = """
            UPDATE Datos_Observacion_001
            SET Magnitud_Aparente = ?, Distancia_Relativa = ?, Velocidad = ?
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
              AND Fecha_Hora = ? AND Id_Observatorio = 1
        """
        return db.execute(sql, (
            data["Magnitud_Aparente"], data["Distancia_Relativa"],
            data["Velocidad"],
            pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"],
        ))

    elif db.sede == "espana":
        statements = [(
            """
            UPDATE Datos_Observacion_002
            SET Magnitud_Aparente = ?, Distancia_Relativa = ?, Velocidad = ?
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
              AND Fecha_Hora = ? AND Id_Observatorio = 2
            """,
            (data["Magnitud_Aparente"], data["Distancia_Relativa"],
             data["Velocidad"],
             pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
        )]

        # Sincronizar extensión vertical: upsert manual (DELETE + INSERT)
        statements.append((
            """
            DELETE FROM Datos_Espectral
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
              AND Fecha_Hora = ? AND Id_Observatorio = 2
            """,
            (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
        ))

        tipo = data.get("Tipo_Espectral")
        if tipo:
            statements.append((
                """
                INSERT INTO Datos_Espectral
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                     Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"],
                 pk["Fecha_Hora"], tipo),
            ))

        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")


# --------------------------------------------------------------------- #
# DELETE
# --------------------------------------------------------------------- #
def delete_observacion(db, pk):
    if db.sede == "chile":
        sql = """
            DELETE FROM Datos_Observacion_001
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
              AND Fecha_Hora = ? AND Id_Observatorio = 1
        """
        return db.execute(sql, (
            pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"],
        ))

    elif db.sede == "espana":
        # Primero la extensión vertical (integridad referencial), luego la base.
        statements = [
            (
                """
                DELETE FROM Datos_Espectral
                WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
                  AND Fecha_Hora = ? AND Id_Observatorio = 2
                """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
            ),
            (
                """
                DELETE FROM Datos_Observacion_002
                WHERE Cod_Cientifico = ? AND Id_Asteroide = ?
                  AND Fecha_Hora = ? AND Id_Observatorio = 2
                """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
            ),
        ]
        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")
