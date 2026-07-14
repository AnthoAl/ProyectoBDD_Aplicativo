"""
ui_components/observations_chile.py
-----------------------------------
Componente de observaciones para el NODO 1 · CHILE (Paranal).

Reglas del nodo:
  * Columnas básicas únicamente:
    [#, Científico, Asteroide, Fecha UTC, Mag. Aparente, Distancia Rel., Velocidad]
  * El formulario NO incluye el campo "Tipo Espectral".
  * Todas las lecturas / escrituras filtran por Id_Observatorio = 1
    (fragmentación horizontal primaria) — ver models/observaciones.py.
"""

from models import asteroides, cientificos, observaciones
from ui_components.base_crud_view import BaseCrudView

COLUMNS = [
    {"key": "num", "title": "#", "weight": 1, "anchor": "center", "min": 40},
    {"key": "cient", "title": "CIENTÍFICO", "weight": 4, "anchor": "w"},
    {"key": "aster", "title": "ASTEROIDE", "weight": 4, "anchor": "w"},
    {"key": "fecha", "title": "FECHA UTC", "weight": 4, "anchor": "center"},
    {"key": "mag", "title": "MAG. APARENTE", "weight": 3, "anchor": "center"},
    {"key": "dist", "title": "DISTANCIA REL.", "weight": 3, "anchor": "center"},
    {"key": "vel", "title": "VELOCIDAD", "weight": 3, "anchor": "center"},
]


class ObservationsChile(BaseCrudView):
    view_title = "Observaciones — Nodo Chile"
    entity_name = "observación"

    def __init__(self, master, db):
        self._cient_map = {}
        self._aster_map = {}
        super().__init__(master, db, COLUMNS)

    # ------------------------- READ ------------------------- #
    def fetch_rows(self):
        # Catálogos para los dropdowns del modal
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
        return observaciones.get_observaciones(self.db)

    def format_row(self, row, index):
        return (
            index + 1,
            row.get("Cientifico") or row.get("Cod_Cientifico"),
            row.get("Asteroide") or row.get("Id_Asteroide"),
            str(row.get("Fecha_Hora", ""))[:16],
            row.get("Magnitud_Aparente", ""),
            row.get("Distancia_Relativa", ""),
            row.get("Velocidad", ""),
        )

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
                    "widget": "entry",
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
        # NOTA: sin campo "Tipo Espectral" — el Nodo Chile no maneja
        # datos espectrales.
        return fields

    # ---------------------- Escrituras ---------------------- #
    def _payload(self, data):
        return {
            "Magnitud_Aparente": float(data["Magnitud_Aparente"]),
            "Distancia_Relativa": float(data["Distancia_Relativa"]),
            "Velocidad": float(data["Velocidad"]),
        }

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
