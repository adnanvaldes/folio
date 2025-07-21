import sqlite3
import datetime as dt
from typing import Optional, List

from .sqlite import SQLiteRepository
from folio.models import Travel
from folio.common import normalize_date


class SQLiteTravelRepository(SQLiteRepository[Travel]):

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def add(self, travel: Travel) -> int:
        self.conn.execute(
            """INSERT INTO travel (
            origin,
            destination,
            date,
            notes
            ) VALUES (?, ?, ?, ?)""",
            (travel.origin, travel.destination, travel.date.isoformat(), travel.notes),
        )

    def get(self, travel_id: int) -> Optional[Travel]:
        row = self.conn.execute(
            "SELECT origin, destination, date, notes FROM travel WHERE id = ?",
            (travel_id,),
        ).fetchone()

        return self._map_row(row) if row else None

    def list(self) -> List[Travel]:
        rows = self.conn.execute(
            "SELECT origin, destination, date, notes FROM travel"
        ).fetchall()

        return [self._map_row(row) for row in rows]

    def find(
        self, origin: str = None, destination: str = None, date: dt.date = None
    ) -> List[Travel]:
        query = "SELECT origin, destination, date, notes FROM travel"
        conditions = []
        params = []

        if origin:
            conditions.append("origin = ?")
            params.append(origin)

        if destination:
            conditions.append("destination = ?")
            params.append(destination)

        if date:
            date_input = normalize_date(date)
            conditions.append("date = ?")
            params.append(date_input)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        rows = self.conn.execute(query, params).fetchall()
        return [self._map_row(row) for row in rows]

    def _map_row(self, row) -> Travel:
        data = dict(row)
        data["date"] = dt.date.fromisoformat(data["date"])
        return Travel(**data)

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
        CREATE TABLE IF NOT EXISTS travel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            CHECK(length(origin) = 3 AND origin = UPPER(origin)),
            CHECK(length(destination) = 3 AND destination = UPPER(destination)),
            UNIQUE(origin, destination, date)
            )
        """
        )
