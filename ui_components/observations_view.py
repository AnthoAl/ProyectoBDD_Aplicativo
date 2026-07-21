"""
ui_components/observations_view.py
-----------------------------------
Vista ÚNICA de observaciones para ambas sedes (reemplaza a
observations_chile.py / observations_spain.py).

Incluye un filtro de SEDE (CHILE / ESPAÑA / AMBAS) que solo controla
qué se MUESTRA, apoyado en VistaGlobalObservaciones (vista particionada
global): sea cual sea el nodo al que esté conectado el operador, puede
leer los registros de cualquiera de los dos nodos o de ambos a la vez.

Reglas de escritura (no dependen del filtro de lectura, sino del nodo
realmente conectado — self.db.sede):
  * AGREGAR siempre crea el registro en el nodo local conectado.
  * El campo "Tipo Espectral" (extensión vertical, exclusiva de España)
    solo aparece en el formulario si el nodo conectado es España.
  * MODIFICAR / BORRAR solo están habilitados sobre filas que pertenecen
    al nodo local conectado, para preservar la atomicidad de la
    extensión vertical Datos_Espectral (ver models/observaciones.py).
"""

from config import TIPOS_ESPECTRALES
from models import asteroides, cientificos, observaciones
from ui_components.base_crud_view import BaseCrudView
from ui_components.sede_filter_mixin import SedeFilterMixin

SIN_ESPECTRO = "— (sin dato)"

COLUMNS = [
    {"key": "num", "title": "#", "weight": 1, "anchor": "center", "min": 40},
    {"key": "sede", "title": "SEDE", "weight": 2, "anchor": "center", "min": 80},
    {"key": "cient", "title": "CIENTÍFICO", "weight": 4, "anchor": "w"},
    {"key": "aster", "title": "ASTEROIDE", "weight": 4, "anchor": "w"},
    {"key": "fecha", "title": "FECHA UTC", "weight": 4, "anchor": "center"},
    {"key": "mag", "title": "MAG. APARENTE (Brillo)", "weight": 3, "anchor": "center"},
    {"key": "dist", "title": "DISTANCIA REL. (UA)", "weight": 3, "anchor": "center"},
    {"key": "vel", "title": "VELOCIDAD (km/s)", "weight": 3, "anchor": "center"},
    {"key": "spec", "title": "◆ TIPO ESPECTRAL", "weight": 3, "anchor": "center"},
]


class ObservationsView(SedeFilterMixin, BaseCrudView):
    view_title = "Observaciones"
    entity_name = "observación"

    def __init__(self, master, db):
        self._cient_map = {}
        self._aster_map = {}
        self._init_sede_filter(db)
        super().__init__(master, db, COLUMNS)

    # ------------------------- READ ------------------------- #
    def fetch_rows(self):
        # Catálogos para los dropdowns del modal (siempre del nodo local).
        self._cient_map = {
            f"{c['Cod_Cientifico']} — {c['Primer_Nombre']} {c['Primer_Apellido']}": c[
                "Cod_Cientifico"
            ]
            for c in cientificos.get_cientificos(self.db)
        }
        self._aster_map = {
            f"{a['Id_Asteroide']} — {a['Nombre']}": a["Id_Asteroide"]
            for a in asteroides.get_asteroides(self.db)
        }
        return observaciones.get_observaciones(self.db, self.filtro)

    def format_row(self, row, index):
        sede_label = "CHILE" if row.get("Id_Observatorio") == 1 else "ESPAÑA"
        return (
            index + 1,
            sede_label,
            row.get("Cientifico") or row.get("Cod_Cientifico"),
            row.get("Asteroide") or row.get("Id_Asteroide"),
            str(row.get("Fecha_Hora", ""))[:16],
            row.get("Magnitud_Aparente", ""),
            row.get("Distancia_Relativa", ""),
            row.get("Velocidad", ""),
            row.get("Tipo_Espectral") or "—",
        )

    def row_tags(self, row):
        # Resalta en cian las filas con dato espectral.
        if row.get("Tipo_Espectral"):
            return ["accent"]
        return None

    # ---------------------- Formulario ---------------------- #
    def build_fields(self, row=None):
        editing = row is not None
        cient_opts = list(self._cient_map) or ["—"]
        aster_opts = list(self._aster_map) or ["—"]

        if editing:
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
                    "key": "Id_Asteroide",
                    "label": "Asteroide (PK)",
                    "widget": "entry",
                    "mono": True,
                    "readonly": True,
                    "default": row["Id_Asteroide"],
                },
                {
                    "key": "Fecha_Hora",
                    "label": "Fecha / Hora UTC (PK)",
                    "widget": "entry",
                    "mono": True,
                    "readonly": True,
                    "default": str(row["Fecha_Hora"])[:16],
                },
            ]
        else:
            fields = [
                {
                    "key": "Cod_Cientifico",
                    "label": "Científico",
                    "widget": "dropdown",
                    "values": cient_opts,
                    "mono": True,
                },
                {
                    "key": "Id_Asteroide",
                    "label": "Asteroide",
                    "widget": "dropdown",
                    "values": aster_opts,
                    "mono": True,
                },
                {
                    "key": "Fecha_Hora",
                    "label": "Fecha / Hora UTC",
                    "widget": "datetime",
                    "mono": True,
                    "placeholder": "YYYY-MM-DD HH:MM",
                },
            ]

        fields += [
            {
                "key": "Magnitud_Aparente",
                "label": "Magnitud aparente",
                "widget": "entry",
                "mono": True,
                "default": row.get("Magnitud_Aparente") if editing else "",
            },
            {
                "key": "Distancia_Relativa",
                "label": "Distancia relativa (UA)",
                "widget": "entry",
                "mono": True,
                "default": row.get("Distancia_Relativa") if editing else "",
            },
            {
                "key": "Velocidad",
                "label": "Velocidad (km/s)",
                "widget": "entry",
                "mono": True,
                "default": row.get("Velocidad") if editing else "",
            },
        ]

        # El Tipo Espectral es la extensión vertical exclusiva del Nodo
        # España: solo se ofrece si el nodo conectado (el que va a
        # recibir la escritura) es España.
        if self.db.sede == "espana":
            opciones_espectrales = [SIN_ESPECTRO] + [
                f"{sigla} — {desc}" for sigla, desc in TIPOS_ESPECTRALES.items()
            ]

            spec_default = SIN_ESPECTRO
            if editing and row.get("Tipo_Espectral"):
                sigla_db = row["Tipo_Espectral"]
                desc_db = TIPOS_ESPECTRALES.get(sigla_db, "")
                spec_default = f"{sigla_db} — {desc_db}" if desc_db else sigla_db

            fields.append({
                "key": "Tipo_Espectral",
                "label": "Tipo espectral",
                "widget": "dropdown",
                "mono": True,
                "values": opciones_espectrales,
                "default": spec_default,
            })

        return fields

    # ---------------------- Escrituras (siempre al nodo local) ---------------------- #
    def _payload(self, data):
        payload = {
            "Magnitud_Aparente": float(data["Magnitud_Aparente"]),
            "Distancia_Relativa": float(data["Distancia_Relativa"]),
            "Velocidad": float(data["Velocidad"]),
        }
        if self.db.sede == "espana":
            tipo_ui = data.get("Tipo_Espectral")
            if tipo_ui in (None, SIN_ESPECTRO):
                payload["Tipo_Espectral"] = None
            else:
                payload["Tipo_Espectral"] = tipo_ui.split(" — ")[0]
        return payload

    def do_insert(self, data):
        payload = self._payload(data)
        payload.update(
            {
                "Cod_Cientifico": self._cient_map.get(
                    data["Cod_Cientifico"], data["Cod_Cientifico"]
                ),
                "Id_Asteroide": self._aster_map.get(
                    data["Id_Asteroide"], data["Id_Asteroide"]
                ),
                "Fecha_Hora": data["Fecha_Hora"],
            }
        )
        observaciones.insert_observacion(self.db, payload)

    def do_update(self, row, data):
        pk = {
            "Cod_Cientifico": row["Cod_Cientifico"],
            "Id_Asteroide": row["Id_Asteroide"],
            "Fecha_Hora": row["Fecha_Hora"],
        }
        observaciones.update_observacion(self.db, pk, self._payload(data))

    def do_delete(self, row):
        pk = {
            "Cod_Cientifico": row["Cod_Cientifico"],
            "Id_Asteroide": row["Id_Asteroide"],
            "Fecha_Hora": row["Fecha_Hora"],
        }
        observaciones.delete_observacion(self.db, pk)