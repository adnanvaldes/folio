import sqlite3
import datetime as dt
from typing import Optional, List

from .sqlite import SQLiteRepository
from folio.models import Address
from folio.common import normalize_date


class SQLiteAddressRepository(SQLiteRepository[Address]):
    RECORD_TYPE = Address
    VALID_FIELDS = (
        "start",
        "end",
        "street",
        "city",
        "province",
        "country",
        "postal_code",
    )

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def _map_row(self, row) -> Address:
        data = dict(row)
        data["start"] = dt.date.fromisoformat(data["start"])
        data["end"] = dt.date.fromisoformat(data["end"]) if data["end"] else None
        return Address(**data)

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
        CREATE TABLE IF NOT EXISTS address (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start TEXT NOT NULL,
            end TEXT,
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            province TEXT,
            country TEXT NOT NULL,
            postal_code TEXT NOT NULL,
            CHECK(end is NULL OR end >= start),
            UNIQUE(street, city, start, end)
        )
            """
        )
