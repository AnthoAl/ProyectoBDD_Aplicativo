"""
ui_components/catalog_views.py
------------------------------
Vistas CRUD para:
  * Tablas GLOBALES REPLICADAS: Asteroide, Programa, Observatorio.
  * Fragmentos locales: Cientifico_00X, Participacion_00X
    (lectura vía vistas particionadas globales filtradas por nodo).
"""

from models import asteroides, cientificos, observatorios, programas
from ui_components.base_crud_view import BaseCrudView
from ui_components.sede_filter_mixin import SedeFilterMixin


# ===================================================================== #
# ASTEROIDES (replicada)
# ===================================================================== #
class AsteroidesView(BaseCrudView):
    view_title = "Asteroides — Catálogo replicado"
    entity_name = "asteroide"

    COLUMNS = [
        {"key": "id", "title": "ID", "weight": 1, "anchor": "center"},
        {"key": "nom", "title": "NOMBRE", "weight": 4, "anchor": "center"},
        {"key": "des", "title": "DESIGNACIÓN", "weight": 3, "anchor": "center"},
        {"key": "diam", "title": "DIÁMETRO EST. (km)", "weight": 3, "anchor": "center"},
        {"key": "pelig", "title": "⚠ PELIGROSO", "weight": 2, "anchor": "center"},
    ]

    def __init__(self, master, db):
        es_maestro = db.sede == "chile"
        super().__init__(
            master,
            db,
            self.COLUMNS,
            allow_create=es_maestro,
            allow_edit=es_maestro,
            allow_delete=es_maestro,
        )

    def fetch_rows(self):
        return asteroides.get_asteroides(self.db)

    def format_row(self, row, index):
        peligroso = row.get("Es_Peligroso")
        return (
            row["Id_Asteroide"],
            row["Nombre"],
            row["Designacion_Provisional"],
            row["Diametro_Estimado"],
            "SÍ ⚠" if peligroso in (1, True, "1") else "NO",
        )

    def row_tags(self, row):
        if row.get("Es_Peligroso") in (1, True, "1"):
            return ["accent"]
        return None

    def build_fields(self, row=None):
        e = row is not None
        return [
            {
                "key": "Id_Asteroide",
                "label": "Id Asteroide (PK)",
                "widget": "entry",
                "mono": True,
                "readonly": e,
                "default": row["Id_Asteroide"] if e else "",
            },
            {
                "key": "Nombre",
                "label": "Nombre",
                "widget": "entry",
                "default": row["Nombre"] if e else "",
            },
            {
                "key": "Designacion_Provisional",
                "label": "Designación",
                "widget": "entry",
                "mono": True,
                "default": row["Designacion_Provisional"] if e else "",
            },
            {
                "key": "Diametro_Estimado",
                "label": "Diámetro estimado (km)",
                "widget": "entry",
                "mono": True,
                "default": row["Diametro_Estimado"] if e else "",
            },
            {
                "key": "Es_Peligroso",
                "label": "¿Es peligroso?",
                "widget": "dropdown",
                "values": ["NO", "SÍ"],
                "default": (
                    "SÍ" if e and row.get("Es_Peligroso") in (1, True, "1") else "NO"
                ),
            },
        ]

    def _payload(self, data):
        return {
            "Id_Asteroide": data["Id_Asteroide"],
            "Nombre": data["Nombre"],
            "Designacion_Provisional": data["Designacion_Provisional"],
            "Diametro_Estimado": float(data["Diametro_Estimado"]),
            "Es_Peligroso": 1 if data["Es_Peligroso"] == "SÍ" else 0,
        }

    def do_insert(self, data):
        asteroides.insert_asteroide(self.db, self._payload(data))

    def do_update(self, row, data):
        payload = self._payload(data)
        payload["Id_Asteroide"] = row["Id_Asteroide"]
        asteroides.update_asteroide(self.db, payload)

    def do_delete(self, row):
        asteroides.delete_asteroide(self.db, row["Id_Asteroide"])


# ===================================================================== #
# PROGRAMAS (replicada)
# ===================================================================== #
class ProgramasView(BaseCrudView):
    view_title = "Programas — Misiones"
    entity_name = "programa"

    COLUMNS = [
        {"key": "id", "title": "ID", "weight": 1, "anchor": "center"},
        {"key": "nom", "title": "MISIÓN", "weight": 5, "anchor": "w"},
        {"key": "pres", "title": "PRESUPUESTO", "weight": 3, "anchor": "center"},
        {"key": "est", "title": "ESTADO", "weight": 2, "anchor": "center"},
    ]
    ESTADOS = ["Activo", "Finalizado"]

    def __init__(self, master, db):
        es_maestro = db.sede == "chile"
        super().__init__(
            master,
            db,
            self.COLUMNS,
            allow_create=es_maestro,
            allow_edit=es_maestro,
            allow_delete=es_maestro,
        )

    def fetch_rows(self):
        return programas.get_programas(self.db)

    def format_row(self, row, index):
        return (
            row["Id_Programa"],
            row["Nombre_Mision"],
            (
                f"$ {row['Presupuesto_asignado']:,}"
                if row.get("Presupuesto_asignado") is not None
                else ""
            ),
            row["Estado"],
        )

    def build_fields(self, row=None):
        e = row is not None
        return [
            {
                "key": "Id_Programa",
                "label": "Id Programa (PK)",
                "widget": "entry",
                "mono": True,
                "readonly": e,
                "default": row["Id_Programa"] if e else "",
            },
            {
                "key": "Nombre_Mision",
                "label": "Nombre de la misión",
                "widget": "entry",
                "default": row["Nombre_Mision"] if e else "",
            },
            {
                "key": "Presupuesto_asignado",
                "label": "Presupuesto (USD)",
                "widget": "entry",
                "mono": True,
                "default": row["Presupuesto_asignado"] if e else "",
            },
            {
                "key": "Estado",
                "label": "Estado",
                "widget": "dropdown",
                "values": self.ESTADOS,
                "default": row["Estado"] if e else self.ESTADOS[0],
            },
        ]

    def _payload(self, data):
        return {
            "Id_Programa": data["Id_Programa"],
            "Nombre_Mision": data["Nombre_Mision"],
            "Presupuesto_asignado": float(data["Presupuesto_asignado"]),
            "Estado": data["Estado"],
        }

    def do_insert(self, data):
        programas.insert_programa(self.db, self._payload(data))

    def do_update(self, row, data):
        payload = self._payload(data)
        payload["Id_Programa"] = row["Id_Programa"]
        programas.update_programa(self.db, payload)

    def do_delete(self, row):
        programas.delete_programa(self.db, row["Id_Programa"])


# ===================================================================== #
# OBSERVATORIOS (replicada)
# ===================================================================== #
class ObservatoriosView(BaseCrudView):
    view_title = "Observatorios — Red global"
    entity_name = "observatorio"

    COLUMNS = [
        {"key": "id", "title": "ID", "weight": 1, "anchor": "center"},
        {"key": "nom", "title": "NOMBRE", "weight": 5, "anchor": "w"},
        {"key": "alt", "title": "ALTITUD (msnm)", "weight": 2, "anchor": "center"},
        {
            "key": "coord",
            "title": "COORDENADAS (lat/lon)",
            "weight": 4,
            "anchor": "center",
        },
        {"key": "cap", "title": "RESOLUCIÓN", "weight": 3, "anchor": "center"},
    ]

    def __init__(self, master, db):
        es_maestro = db.sede == "chile"
        super().__init__(
            master,
            db,
            self.COLUMNS,
            allow_create=es_maestro,
            allow_edit=es_maestro,
            allow_delete=es_maestro,
        )

    def fetch_rows(self):
        return observatorios.get_observatorios(self.db)

    def format_row(self, row, index):
        return (
            row["Id_Observatorio"],
            row["Nombre"],
            row["Altitud"],
            row["Coordenadas"],
            row["Capacidad_Resolucion"],
        )

    def build_fields(self, row=None):
        e = row is not None
        return [
            {
                "key": "Id_Observatorio",
                "label": "Id Observatorio (PK)",
                "widget": "entry",
                "mono": True,
                "readonly": e,
                "default": row["Id_Observatorio"] if e else "",
            },
            {
                "key": "Nombre",
                "label": "Nombre",
                "widget": "entry",
                "default": row["Nombre"] if e else "",
            },
            {
                "key": "Altitud",
                "label": "Altitud (msnm)",
                "widget": "entry",
                "mono": True,
                "default": row["Altitud"] if e else "",
            },
            {
                "key": "Coordenadas",
                "label": "COORDENADAS (lat/lon)",
                "widget": "entry",
                "default": row["Coordenadas"] if e else "",
            },
            {
                "key": "Capacidad_Resolucion",
                "label": "Capacidad de resolución",
                "widget": "entry",
                "mono": True,
                "default": row["Capacidad_Resolucion"] if e else "",
            },
        ]

    def _payload(self, data):
        return {
            "Id_Observatorio": data["Id_Observatorio"],
            "Nombre": data["Nombre"],
            "Altitud": float(data["Altitud"]),
            "Coordenadas": data["Coordenadas"],
            "Capacidad_Resolucion": data["Capacidad_Resolucion"],
        }

    def do_insert(self, data):
        observatorios.insert_observatorio(self.db, self._payload(data))

    def do_update(self, row, data):
        payload = self._payload(data)
        payload["Id_Observatorio"] = row["Id_Observatorio"]
        observatorios.update_observatorio(self.db, payload)

    def do_delete(self, row):
        observatorios.delete_observatorio(self.db, row["Id_Observatorio"])


# ===================================================================== #
# CIENTÍFICOS (fragmento local; filtro CHILE / ESPAÑA / AMBAS)
# ===================================================================== #
class CientificosView(SedeFilterMixin, BaseCrudView):
    view_title = "Científicos"
    entity_name = "científico"

    COLUMNS = [
        {"key": "cod", "title": "CÓDIGO", "weight": 2, "anchor": "center"},
        {"key": "sede", "title": "SEDE", "weight": 2, "anchor": "center"},
        {"key": "nom", "title": "PRIMER NOMBRE", "weight": 5, "anchor": "w"},
        {"key": "ape", "title": "PRIMER APELLIDO", "weight": 5, "anchor": "w"},
        {"key": "esp", "title": "ESPECIALIDAD", "weight": 4, "anchor": "w"},
        {"key": "nac", "title": "NACIONALIDAD", "weight": 4, "anchor": "w"},
    ]

    def __init__(self, master, db):
        self._init_sede_filter(db)
        super().__init__(master, db, self.COLUMNS)

    def fetch_rows(self):
        return cientificos.get_cientificos(self.db, self.filtro)

    def format_row(self, row, index):
        sede_label = "CHILE" if row.get("Id_Observatorio") == 1 else "ESPAÑA"
        return (
            row["Cod_Cientifico"],
            sede_label,
            row["Primer_Nombre"],
            row["Primer_Apellido"],
            row.get("Especialidad", ""),
            row["Nacionalidad"],
        )

    def build_fields(self, row=None):
        e = row is not None
        return [
            {
                "key": "Cod_Cientifico",
                "label": "Código científico (PK)",
                "widget": "entry",
                "mono": True,
                "readonly": e,
                "default": row["Cod_Cientifico"] if e else "",
            },
            {
                "key": "Primer_Nombre",
                "label": "Primer nombre",
                "widget": "entry",
                "default": row["Primer_Nombre"] if e else "",
            },
            {
                "key": "Primer_Apellido",
                "label": "Primer apellido",
                "widget": "entry",
                "default": row["Primer_Apellido"] if e else "",
            },
            {
                "key": "Especialidad",
                "label": "Especialidad",
                "widget": "entry",
                "default": row.get("Especialidad", "") if e else "",
            },
            {
                "key": "Nacionalidad",
                "label": "Nacionalidad",
                "widget": "entry",
                "default": row["Nacionalidad"] if e else "",
            },
        ]

    def do_insert(self, data):
        cientificos.insert_cientifico(self.db, data)

    def do_update(self, row, data):
        data = dict(data)
        data["Cod_Cientifico"] = row["Cod_Cientifico"]
        cientificos.update_cientifico(self.db, data)

    def do_delete(self, row):
        cientificos.delete_cientifico(self.db, row["Cod_Cientifico"])


# ===================================================================== #
# PARTICIPACIONES (fragmento local; filtro CHILE / ESPAÑA / AMBAS;
# sin UPDATE de las PK por ser tabla puente)
# ===================================================================== #
class ParticipacionesView(SedeFilterMixin, BaseCrudView):
    view_title = "Participaciones — Científico ⇄ Programa"
    entity_name = "participación"

    COLUMNS = [
        {"key": "cod", "title": "CÓD.", "weight": 1, "anchor": "center"},
        {"key": "sede", "title": "SEDE", "weight": 2, "anchor": "center"},
        {"key": "nomc", "title": "CIENTÍFICO", "weight": 4, "anchor": "w"},
        {"key": "idp", "title": "ID PROG.", "weight": 1, "anchor": "center"},
        {"key": "ini", "title": "INICIO", "weight": 3, "anchor": "center"},
        {"key": "fin", "title": "FIN", "weight": 3, "anchor": "center"},
        {"key": "mis", "title": "ROL", "weight": 4, "anchor": "w"},
    ]

    def __init__(self, master, db):
        self._cient_map = {}
        self._prog_map = {}
        self._init_sede_filter(db)
        super().__init__(master, db, self.COLUMNS, allow_edit=True)

    def fetch_rows(self):
        # Los dropdowns del modal solo ofrecen científicos/programas
        # con los que se puede escribir desde el nodo local conectado.
        self._cient_map = {
            f"{c['Cod_Cientifico']} — {c['Primer_Nombre']} {c['Primer_Apellido']}": c[
                "Cod_Cientifico"
            ]
            for c in cientificos.get_cientificos(self.db)
        }
        self._prog_map = {
            f"{p['Id_Programa']} — {p['Nombre_Mision']}": p["Id_Programa"]
            for p in programas.get_programas(self.db)
        }
        return cientificos.get_participaciones(self.db, self.filtro)

    def format_row(self, row, index):
        sede_label = "CHILE" if row.get("Id_Observatorio") == 1 else "ESPAÑA"
        return (
            row["Cod_Cientifico"],
            sede_label,
            row.get("Cientifico") or "",
            row["Id_Programa"],
            str(row.get("Fecha_Inicio", ""))[
                :10
            ],  # Cortamos la fecha para que se vea YYYY-MM-DD
            str(row.get("Fecha_Fin", ""))[:10],
            row["Rol_En_Mision"],
        )

    def build_fields(self, row=None):
        editing = row is not None

        cient_opts = list(self._cient_map.keys()) or ["—"]
        prog_opts = list(self._prog_map.keys()) or ["—"]

        if editing:
            # Si estamos editando, las llaves primarias se vuelven cajas de texto bloqueadas
            fields = [
                {
                    "key": "Cod_Cientifico",
                    "label": "Científico (PK)",
                    "widget": "entry",
                    "mono": True,
                    "readonly": True,
                    "default": row["Cod_Cientifico"],
                },
                {
                    "key": "Id_Programa",
                    "label": "Id Programa (PK)",
                    "widget": "entry",
                    "mono": True,
                    "readonly": True,
                    "default": row["Id_Programa"],
                },
                {
                    "key": "Fecha_Inicio",
                    "label": "Fecha de Inicio (PK)",
                    "widget": "entry",
                    "mono": True,
                    "readonly": True,
                    "default": str(row.get("Fecha_Inicio", ""))[:10],
                },
            ]
        else:
            # Si es un nuevo registro, mostramos los dropdowns y el calendario
            fields = [
                {
                    "key": "Cod_Cientifico",
                    "label": "Científico",
                    "widget": "dropdown",
                    "mono": True,
                    "values": cient_opts,
                },
                {
                    "key": "Id_Programa",
                    "label": "Programa",
                    "widget": "dropdown",
                    "mono": True,
                    "values": prog_opts,
                },
                {
                    "key": "Fecha_Inicio",
                    "label": "Fecha de Inicio",
                    "widget": "date",
                    "mono": True,
                },
            ]

        # Campos comunes que SIEMPRE se pueden editar
        fields += [
            {
                "key": "Fecha_Fin",
                "label": "Fecha de Fin (Opcional)",
                "widget": "date",
                "mono": True,
                "required": False,
                "default": (
                    str(row.get("Fecha_Fin", ""))[:10]
                    if editing and row.get("Fecha_Fin")
                    else ""
                ),
            },
            {
                "key": "Rol_En_Mision",
                "label": "Rol en la Misión (Opcional)",
                "widget": "entry",
                "mono": False,
                "required": False,
                "placeholder": "Ej. Investigador Principal",
                "default": row.get("Rol_En_Mision", "") if editing else "",
            },
        ]
        return fields

    def do_insert(self, data):
        cientificos.insert_participacion(
            self.db,
            {
                "Cod_Cientifico": self._cient_map.get(
                    data["Cod_Cientifico"], data["Cod_Cientifico"]
                ),
                "Id_Programa": self._prog_map.get(
                    data["Id_Programa"], data["Id_Programa"]
                ),
                "Fecha_Inicio": data["Fecha_Inicio"],
                # "Id_Observatorio": data["Id_Observatorio"],
                "Fecha_Fin": data["Fecha_Fin"],
                "Rol_En_Mision": data["Rol_En_Mision"],
            },
        )

    def do_update(self, row, data):
        # 1. Extraemos las llaves primarias de la fila original
        pk = {
            "Cod_Cientifico": row["Cod_Cientifico"],
            "Id_Programa": row["Id_Programa"],
            "Fecha_Inicio": row["Fecha_Inicio"],
        }

        # 2. Manejamos los campos vacíos para que viajen como NULL a SQL Server
        payload = {
            "Fecha_Fin": (
                data["Fecha_Fin"] if data.get("Fecha_Fin", "").strip() != "" else None
            ),
            "Rol_En_Mision": (
                data["Rol_En_Mision"]
                if data.get("Rol_En_Mision", "").strip() != ""
                else None
            ),
        }

        # 3. Enviamos a la base de datos
        cientificos.update_participacion(self.db, pk, payload)

    def do_delete(self, row):
        cientificos.delete_participacion(
            self.db, row["Cod_Cientifico"], row["Id_Programa"], row["Fecha_Inicio"]
        )