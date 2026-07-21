"""
models/observaciones.py
-----------------------
Fragmentos horizontales:
    Nodo 1 (Chile)  : Datos_Observacion_001  (SIN datos espectrales)
    Nodo 2 (España) : Datos_Observacion_002 + extensión vertical Datos_Espectral
                      [Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                       Id_Observatorio, Tipo_Espectral]

Lecturas:
    - VistaGlobalObservaciones, con LEFT JOIN permanente a Datos_Espectral
      (fragmentación vertical), filtrable por sede vía el parámetro
      `filtro` de get_observaciones(): "chile" (Id_Observatorio = 1),
      "espana" (Id_Observatorio = 2) o "ambas" (sin filtro, federando
      los dos nodos gracias a la transparencia de la vista particionada).

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
        {where_clause}
        ORDER BY O.Fecha_Hora DESC
    """
    return db.fetch_all(sql)
# --------------------------------------------------------------------- #
# CREATE
# --------------------------------------------------------------------- #
def insert_observacion(db, data):
    base_sql = """
        INSERT INTO VistaGlobalObservaciones
            (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio,
             Magnitud_Aparente, Distancia_Relativa, Velocidad_Aproximada)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    # Mapeamos data["Velocidad"] (viene de la UI) al campo de la BD
    base_params = (
        data["Cod_Cientifico"],
        data["Id_Asteroide"],
        data["Fecha_Hora"],
        db.cfg["id_observatorio"],
        data["Magnitud_Aparente"],
        data["Distancia_Relativa"],
        data["Velocidad"],
    )

    if db.sede == "chile":
        return db.execute(base_sql, base_params)

    elif db.sede == "espana":
        # España requiere atomicidad con la tabla de extensión vertical
        statements = [(base_sql, base_params)]
        tipo = data.get("Tipo_Espectral")
        if tipo:
            statements.append(
                (
                    """
                INSERT INTO Datos_Espectral
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora,
                     Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                    (
                        data["Cod_Cientifico"],
                        data["Id_Asteroide"],
                        data["Fecha_Hora"],
                        tipo,
                    ),
                )
            )
        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")


# --------------------------------------------------------------------- #
# UPDATE
# --------------------------------------------------------------------- #
def update_observacion(db, pk, data):
    # Transparencia total de ruteo: El WHERE ya no exige saber la Sede
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

    if db.sede == "chile":
        return db.execute(base_sql, base_params)

    elif db.sede == "espana":
        statements = [(base_sql, base_params)]

        # Sincronizamos la extensión vertical (Borrar e insertar de nuevo)
        statements.append(
            (
                """
            DELETE FROM Datos_Espectral
            WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
            """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
            )
        )

        tipo = data.get("Tipo_Espectral")
        if tipo:
            statements.append(
                (
                    """
                INSERT INTO Datos_Espectral
                    (Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio, Tipo_Espectral)
                VALUES (?, ?, ?, 2, ?)
                """,
                    (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"], tipo),
                )
            )

        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")


# --------------------------------------------------------------------- #
# DELETE
# --------------------------------------------------------------------- #
def delete_observacion(db, pk):
    # Transparencia total de ruteo: El WHERE ya no exige saber la Sede
    base_sql = """
        DELETE FROM VistaGlobalObservaciones
        WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
    """
    base_params = (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"])

    if db.sede == "chile":
        return db.execute(base_sql, base_params)

    elif db.sede == "espana":
        # Primero borramos la dependencia (Datos_Espectral) por integridad referencial
        statements = [
            (
                """
                DELETE FROM Datos_Espectral
                WHERE Cod_Cientifico = ? AND Id_Asteroide = ? AND Fecha_Hora = ?
                """,
                (pk["Cod_Cientifico"], pk["Id_Asteroide"], pk["Fecha_Hora"]),
            ),
            (base_sql, base_params),
        ]
        return db.execute_transaction(statements)

    else:
        raise ValueError(f"Sede no soportada: {db.sede!r}")
