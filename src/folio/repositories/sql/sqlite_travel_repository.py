import sqlite3
import datetime as dt
from typing import Optional, List

from .sqlite import SQLiteRepository
from folio.models import Travel
from folio.common import normalize_date


class SQLiteTravelRepository(SQLiteRepository[Travel]):
    RECORD_TYPE = Travel
    VALID_FIELDS = ("origin", "destination", "date", "notes")

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

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
