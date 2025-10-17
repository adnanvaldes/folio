import sqlite3
import datetime as dt

from .sqlite import SQLiteRepository
from folio.models import Employment
from folio.common import normalize_date


class SQLiteEmploymentRepository(SQLiteRepository[Employment]):
    RECORD_TYPE = Employment
    VALID_FIELDS = ("start", "end", "company", "supervisor", "address", "phone")

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def _map_row(self, row) -> Employment:
        data = dict(row)
        data["start"] = dt.date.fromisoformat(data["start"])
        data["end"] = dt.date.fromisoformat(data["end"]) if data["end"] else None
        return Employment(**data)

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
        CREATE TABLE IF NOT EXISTS employment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT NOT NULL,
            end TEXT,
            company TEXT NOT NULL,
            supervisor TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            CHECK(end IS NULL OR end >= start),
            UNIQUE(company, start)
            )
        """
        )
