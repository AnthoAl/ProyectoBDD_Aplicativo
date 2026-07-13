# NASA / PDCO — Base de Datos Distribuida (Monitoreo de Asteroides)

Aplicación de escritorio en Python (`customtkinter` + `ttk.Treeview` + `pyodbc` / SQL Server) para la gestión de una BDD híbrida con tablas replicadas y fragmentadas geográficamente (Nodo 1 · Chile — Paranal / Nodo 2 · España — Roque de los Muchachos).

## Estructura

```
nasa_dds/
├── main.py                  # Orquestador: login, shell, ruteo if/elif/else
├── config.py                # Nodos, credenciales, condición de fragmentación
├── theme.py                 # Paleta Figma + estilo del ttk.Treeview
├── db_connection.py         # pyodbc: fetch_all / execute / execute_transaction
├── models/
│   ├── asteroides.py        # Tabla replicada Asteroide
│   ├── programas.py         # Tabla replicada Programa
│   ├── observatorios.py     # Tabla replicada Observatorio
│   ├── cientificos.py       # Fragmentos Cientifico_00X / Participacion_00X
│   └── observaciones.py     # Fragmentos Datos_Observacion_00X + Datos_Espectral
└── ui_components/
    ├── login_view.py        # Selección de sede (define self.sede)
    ├── sidebar.py           # Navegación
    ├── topbar.py            # Título de vista + reloj UTC
    ├── data_table.py        # Treeview oscuro con columnas dinámicas
    ├── form_modal.py        # CTkToplevel centrado + grab_set()
    ├── base_crud_view.py    # CRUD genérico + refresco automático
    ├── observations_chile.py# Componente Nodo 1 (sin Tipo Espectral)
    ├── observations_spain.py# Componente Nodo 2 (Tipo Espectral + atomicidad)
    └── catalog_views.py     # Asteroides / Programas / Observatorios / etc.
```

## Instalación

```bash
pip install -r requirements.txt
python main.py
```

Requiere el **ODBC Driver 17 for SQL Server** (o ajustar `driver` en `config.py`).

## Configuración

Edita `config.py`:
- `server` / `database` de cada nodo.
- `trusted = False` + `uid`/`pwd` si usas autenticación SQL.

## Lógica distribuida implementada

| Regla | Dónde |
|---|---|
| Bifurcación por sede (`self.sede`) | `main.py → navigate()` |
| Lecturas vía vistas particionadas globales con `WHERE Id_Observatorio = 1/2` | `models/observaciones.py`, `models/cientificos.py` |
| Escrituras al fragmento local (`_001` / `_002`) | `models/*` |
| Atomicidad en España (`Datos_Observacion_002` + `Datos_Espectral`) | `db_connection.execute_transaction()` |
| Chile sin dominio espectral (ni columna ni campo en el modal) | `observations_chile.py` |
| Dropdown Tipo Espectral (C, S, M, Sq, B, Sk) | `observations_spain.py` |
| DELETE con confirmación + refresco automático del Treeview | `base_crud_view.py` |
| Modales `CTkToplevel` centrados con `grab_set()` | `form_modal.py` |
| Sin `match-case` (solo if/elif/else) | Todo el proyecto |

## Notas de esquema

- Se asume que `Datos_Observacion_00X` incluye las columnas de medición
  `Magnitud_Aparente`, `Distancia_Relativa`, `Velocidad` y la PK compuesta
  `(Cod_Cientifico, Id_Asteroide, Fecha_Hora, Id_Observatorio)`.
- Se asume `Cientifico_00X (Cod_Cientifico, Nombre, Especialidad, Id_Observatorio)`
  y `Participacion_00X (Cod_Cientifico, Id_Programa, Id_Observatorio)`.
- Si tus columnas reales difieren, ajusta **solo** los archivos de `models/`
  (la UI toma los nombres desde ahí).

## Tipografías

Instala **Inter** y **JetBrains Mono** en el sistema para replicar el diseño
Figma; si no están disponibles, la app degrada automáticamente a
Segoe UI / Consolas (`theme.py → _resolve`).

Limitación de `ttk.Treeview`: la fuente es única para todo el cuerpo de la
tabla (no se puede asignar por columna), por lo que los encabezados usan
JetBrains Mono y las celdas Inter.
