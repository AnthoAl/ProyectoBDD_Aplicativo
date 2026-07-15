"""
ui_components/observations_spain.py
-----------------------------------
Componente de observaciones para el NODO 2 · ESPAÑA (Roque de los Muchachos).

Reglas del nodo:
  * Añade al final la columna exclusiva TIPO ESPECTRAL (resaltada en cian
    cuando la observación posee dato espectral).
  * El formulario incluye un Dropdown Tipo_Espectral (C, S, M, Sq, B, Sk).
  * Persistencia ATÓMICA: la observación se inserta en Datos_Observacion_002
    y, si trae tipo espectral, en la extensión vertical Datos_Espectral,
    dentro de la MISMA transacción (WHERE Id_Observatorio = 2).
"""

from config import TIPOS_ESPECTRALES
from models import asteroides, cientificos, observaciones
from ui_components.base_crud_view import BaseCrudView

SIN_ESPECTRO = "— (sin dato)"

COLUMNS = [
    {"key": "num", "title": "#", "weight": 1, "anchor": "center", "min": 40},
    {"key": "cient", "title": "CIENTÍFICO", "weight": 4, "anchor": "w"},
    {"key": "aster", "title": "ASTEROIDE", "weight": 4, "anchor": "w"},
    {"key": "fecha", "title": "FECHA UTC", "weight": 4, "anchor": "center"},
    {"key": "mag", "title": "MAG. APARENTE (Brillo)", "weight": 3, "anchor": "center"},
    {"key": "dist", "title": "DISTANCIA REL. (UA)", "weight": 3, "anchor": "center"},
    {"key": "vel", "title": "VELOCIDAD (km/s)", "weight": 3, "anchor": "center"},
    {"key": "spec", "title": "◆ TIPO ESPECTRAL", "weight": 3, "anchor": "center"},
]


class ObservationsSpain(BaseCrudView):
    view_title = "Observaciones — Nodo España"
    entity_name = "observación"

    def __init__(self, master, db):
        self._cient_map = {}
        self._aster_map = {}
        super().__init__(master, db, COLUMNS)

    # ------------------------- READ ------------------------- #
    def fetch_rows(self):
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
            row.get("Tipo_Espectral") or "—",
        )

    def row_tags(self, row):
        # Resalta en cian las filas con dato espectral (columna exclusiva).
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
                    "mono": True,  # <-- Usando el datetime que creamos
                    "placeholder": "YYYY-MM-DD HH:MM",
                },
            ]

        # 1. Construimos las opciones visuales (Ej: "C — Carbonáceo (Oscuro)")
        opciones_espectrales = [SIN_ESPECTRO] + [
            f"{sigla} — {desc}" for sigla, desc in TIPOS_ESPECTRALES.items()
        ]

        spec_default = SIN_ESPECTRO
        if editing and row.get("Tipo_Espectral"):
            sigla_db = row["Tipo_Espectral"]
            # 2. Reconstruimos el string visual para pre-seleccionar el dropdown al Modificar
            desc_db = TIPOS_ESPECTRALES.get(sigla_db, "")
            spec_default = f"{sigla_db} — {desc_db}" if desc_db else sigla_db

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
            # ---- Campo EXCLUSIVO del Nodo 2 (extensión vertical) ----
            {
                "key": "Tipo_Espectral",
                "label": "Tipo espectral",
                "widget": "dropdown",
                "mono": True,
                "values": opciones_espectrales,
                "default": spec_default,
            },
        ]
        return fields

    # ---------------------- Escrituras ---------------------- #
    def _payload(self, data):
        tipo_ui = data.get("Tipo_Espectral")

        # 3. Al guardar, extraemos únicamente la sigla aislando lo que está antes del " — "
        if tipo_ui == SIN_ESPECTRO or not tipo_ui:
            tipo_db = None
        else:
            tipo_db = tipo_ui.split(" — ")[0]

        return {
            "Magnitud_Aparente": float(data["Magnitud_Aparente"]),
            "Distancia_Relativa": float(data["Distancia_Relativa"]),
            "Velocidad": float(data["Velocidad"]),
            "Tipo_Espectral": tipo_db,
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
        # Transacción atómica: Datos_Observacion_002 (+ Datos_Espectral)
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
