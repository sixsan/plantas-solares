import sqlite3
from typing import List, Optional
from src.Model.InversorSpecs import InversorSpecs


class InversorSpecsRepository:
    """Repositorio para la persistencia de InversorSpecs en SQLite."""

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
        """Crea la tabla inversor_specs si no existe."""
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
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
        finally:
            self._close_conn(conn)

    def _row_to_inversor(self, row: sqlite3.Row) -> InversorSpecs:
        return InversorSpecs(
            id=row["id"],
            modelo=row["modelo"],
            potencia_nominal_kw=float(row["potencia_nominal_kw"]),
            eficiencia_porc=float(row["eficiencia_porc"]),
        )

    def create(self, inversor: InversorSpecs) -> InversorSpecs:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO inversor_specs (id, modelo, potencia_nominal_kw, eficiencia_porc)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        inversor.id,
                        inversor.modelo,
                        inversor.potencia_nominal_kw,
                        inversor.eficiencia_porc,
                    ),
                )
            return inversor
        finally:
            self._close_conn(conn)

    def get_by_id(self, id: str) -> Optional[InversorSpecs]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, modelo, potencia_nominal_kw, eficiencia_porc
                FROM inversor_specs
                WHERE id = ?
                """,
                (id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_inversor(row)
        finally:
            self._close_conn(conn)

    def get_all(self) -> List[InversorSpecs]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, modelo, potencia_nominal_kw, eficiencia_porc
                FROM inversor_specs
                """
            )
            rows = cursor.fetchall()
            return [self._row_to_inversor(row) for row in rows]
        finally:
            self._close_conn(conn)

    def update(self, inversor: InversorSpecs) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE inversor_specs
                    SET modelo = ?, potencia_nominal_kw = ?, eficiencia_porc = ?
                    WHERE id = ?
                    """,
                    (
                        inversor.modelo,
                        inversor.potencia_nominal_kw,
                        inversor.eficiencia_porc,
                        inversor.id,
                    ),
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
                    DELETE FROM inversor_specs
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
                SELECT 1 FROM inversor_specs WHERE id = ?
                """,
                (id,),
            )
            return cursor.fetchone() is not None
        finally:
            self._close_conn(conn)
