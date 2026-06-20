import sqlite3

from .sqlite import SQLiteRepository
from folio.models import Work


class SQLiteWorkRepository(SQLiteRepository[Work]):
    RECORD_TYPE = Work
    VALID_FIELDS = ("title", "author", "year", "genre", "is_read")

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def _map_row(self, row) -> Work:
        data = dict(row)
        data["is_read"] = bool(data["is_read"])
        return Work(**data)

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
        CREATE TABLE IF NOT EXISTS work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            is_read INTEGER NOT NULL CHECK(is_read IN (0,1)),
            UNIQUE(title, author, year))
        """
        )
