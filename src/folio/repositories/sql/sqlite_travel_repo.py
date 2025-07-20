import sqlite3
from datetime import date

from .sqlite import SQLiteRepository
from folio.models import Travel


class SQLiteTravelRepo(SQLiteRepository[Travel]):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
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
            (travel_id),
        ).fetchone()

        if not row:
            return None

        data = dict(row)
        data["date"] = date.fromisoformat(data["date"])
        return Travel(**data)

    def list(self) -> List[Travel]:
        rows = self.conn.execute(
            "SELECT origin, destination, date, notes FROM travel"
        ).fetchall()

        travels = []
        for row in rows:
            data = dict(row)
            date["date"] = date.fromisoformat(data["date"])
            travels.append(Travel(**data))

        return travels

    def ensure_table(self) -> None:
        self.conn.execute(
            """
        CREATE TABLE IF NOT EXISTS travel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            notes TEXT
            )
        """
        )
