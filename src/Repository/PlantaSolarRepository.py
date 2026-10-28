import sqlite3
from typing import List, Optional
from src.Model.Coordenadas import Coordenadas
from src.Model.InversorSpecs import InversorSpecs
from src.Model.PlantaSolar import PlantaSolar


class PlantaSolarRepository:
    """Repositorio para la persistencia de PlantaSolar con Coordenadas e InversorSpecs en SQLite."""

    def __init__(self, db_path: str = "plantas_solares.db"):
        self.db_path = db_path
        self._memory_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        if self._memory_conn is not None:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _close_conn(self, conn: sqlite3.Connection) -> None:
        if conn != self._memory_conn:
            conn.close()

    def _ensure_schema(self) -> None:
        """Crea las tablas y asegura que existan las columnas correspondientes."""
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # Tabla inversor_specs
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS inversor_specs (
                        id TEXT PRIMARY KEY,
                        modelo TEXT NOT NULL,
                        potencia_nominal_kw REAL NOT NULL,
                        eficiencia_porc REAL NOT NULL
                    )
                    """
                )

                # Tabla plantas_solares
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plantas_solares (
                        id TEXT PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        potencia_dc_kw REAL NOT NULL,
                        latitud REAL,
                        longitud REAL,
                        altitud_m REAL,
                        inversor_specs_id TEXT
                    )
                    """
                )
                # Migración automática si las columnas fueron creadas previamente sin coordenadas o inversor
                cursor.execute("PRAGMA table_info(plantas_solares)")
                columnas = {row["name"] for row in cursor.fetchall()}
                if "latitud" not in columnas:
                    cursor.execute("ALTER TABLE plantas_solares ADD COLUMN latitud REAL")
                if "longitud" not in columnas:
                    cursor.execute("ALTER TABLE plantas_solares ADD COLUMN longitud REAL")
                if "altitud_m" not in columnas:
                    cursor.execute("ALTER TABLE plantas_solares ADD COLUMN altitud_m REAL")
                if "inversor_specs_id" not in columnas:
                    cursor.execute("ALTER TABLE plantas_solares ADD COLUMN inversor_specs_id TEXT")
        finally:
            self._close_conn(conn)

    def _row_to_planta(self, row: sqlite3.Row) -> PlantaSolar:
        coordenadas = None
        row_keys = row.keys()
        if (
            "latitud" in row_keys
            and row["latitud"] is not None
            and row["longitud"] is not None
            and row["altitud_m"] is not None
        ):
            coordenadas = Coordenadas(
                latitud=float(row["latitud"]),
                longitud=float(row["longitud"]),
                altitud_m=float(row["altitud_m"]),
            )

        inversor_specs = None
        if "inv_id" in row_keys and row["inv_id"] is not None:
            inversor_specs = InversorSpecs(
                id=row["inv_id"],
                modelo=row["inv_modelo"],
                potencia_nominal_kw=float(row["inv_potencia_nominal_kw"]),
                eficiencia_porc=float(row["inv_eficiencia_porc"]),
            )

        return PlantaSolar(
            id=row["id"],
            nombre=row["nombre"],
            potencia_dc_kw=float(row["potencia_dc_kw"]),
            coordenadas=coordenadas,
            inversor_specs=inversor_specs,
        )

    def create(self, planta: PlantaSolar) -> PlantaSolar:
        conn = self._get_connection()
        lat = planta.coordenadas.latitud if planta.coordenadas else None
        lon = planta.coordenadas.longitud if planta.coordenadas else None
        alt = planta.coordenadas.altitud_m if planta.coordenadas else None
        inv_id = planta.inversor_specs.id if planta.inversor_specs else None

        try:
            with conn:
                cursor = conn.cursor()
                if planta.inversor_specs:
                    cursor.execute("SELECT 1 FROM inversor_specs WHERE id = ?", (planta.inversor_specs.id,))
                    if cursor.fetchone() is None:
                        raise ValueError(f"No existe ningún inversor con el id '{planta.inversor_specs.id}'.")

                cursor.execute(
                    """
                    INSERT INTO plantas_solares (id, nombre, potencia_dc_kw, latitud, longitud, altitud_m, inversor_specs_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (planta.id, planta.nombre, planta.potencia_dc_kw, lat, lon, alt, inv_id),
                )
            return planta
        finally:
            self._close_conn(conn)

    def get_by_id(self, id: str) -> Optional[PlantaSolar]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    p.id, p.nombre, p.potencia_dc_kw, p.latitud, p.longitud, p.altitud_m, p.inversor_specs_id,
                    i.id AS inv_id, i.modelo AS inv_modelo, i.potencia_nominal_kw AS inv_potencia_nominal_kw, i.eficiencia_porc AS inv_eficiencia_porc
                FROM plantas_solares p
                LEFT JOIN inversor_specs i ON p.inversor_specs_id = i.id
                WHERE p.id = ?
                """,
                (id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_planta(row)
        finally:
            self._close_conn(conn)

    def get_all(self) -> List[PlantaSolar]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    p.id, p.nombre, p.potencia_dc_kw, p.latitud, p.longitud, p.altitud_m, p.inversor_specs_id,
                    i.id AS inv_id, i.modelo AS inv_modelo, i.potencia_nominal_kw AS inv_potencia_nominal_kw, i.eficiencia_porc AS inv_eficiencia_porc
                FROM plantas_solares p
                LEFT JOIN inversor_specs i ON p.inversor_specs_id = i.id
                """
            )
            rows = cursor.fetchall()
            return [self._row_to_planta(row) for row in rows]
        finally:
            self._close_conn(conn)

    def update(self, planta: PlantaSolar) -> bool:
        conn = self._get_connection()
        lat = planta.coordenadas.latitud if planta.coordenadas else None
        lon = planta.coordenadas.longitud if planta.coordenadas else None
        alt = planta.coordenadas.altitud_m if planta.coordenadas else None
        inv_id = planta.inversor_specs.id if planta.inversor_specs else None

        try:
            with conn:
                cursor = conn.cursor()
                if planta.inversor_specs:
                    cursor.execute("SELECT 1 FROM inversor_specs WHERE id = ?", (planta.inversor_specs.id,))
                    if cursor.fetchone() is None:
                        raise ValueError(f"No existe ningún inversor con el id '{planta.inversor_specs.id}'.")

                cursor.execute(
                    """
                    UPDATE plantas_solares
                    SET nombre = ?, potencia_dc_kw = ?, latitud = ?, longitud = ?, altitud_m = ?, inversor_specs_id = ?
                    WHERE id = ?
                    """,
                    (planta.nombre, planta.potencia_dc_kw, lat, lon, alt, inv_id, planta.id),
                )
                return cursor.rowcount > 0
        finally:
            self._close_conn(conn)

    def delete(self, id: str) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM plantas_solares
                    WHERE id = ?
                    """,
                    (id,),
                )
                return cursor.rowcount > 0
        finally:
            self._close_conn(conn)

    def exists(self, id: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM plantas_solares WHERE id = ?
                """,
                (id,),
            )
            return cursor.fetchone() is not None
        finally:
            self._close_conn(conn)
