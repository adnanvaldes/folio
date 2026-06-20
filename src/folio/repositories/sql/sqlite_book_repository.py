import sqlite3

from .sqlite import SQLiteRepository
from folio.models import Book


class SQLiteBookRepository(SQLiteRepository[Book]):
    RECORD_TYPE = Book
    VALID_FIELDS = ("work_id", "pages", "format", "ISBN")

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
            work_id INTEGER NOT NULL,
            pages INTEGER,
            
        """
        )
