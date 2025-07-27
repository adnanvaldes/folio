import sqlite3
import datetime as dt
from typing import Optional, List

from .sqlite import SQLiteRepository
from folio.models import Employment
from folio.common import normalize_date


class SQLiteEmploymentRepository(SQLiteRepository[Employment]):

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def add(self, employment: Employment) -> int:
        cursor = self.conn.execute(
            """INSERT INTO employment (
            start,
            end,
            company,
            supervisor,
            address,
            phone
        ) VALUES (?, ? ,?, ?, ?, ?)""",
            (
                employment.start,
                employment.end,
                employment.company,
                employment.supervisor,
                employment.address,
                employment.phone,
            ),
        )

        return cursor.lastrowid

    def get(self, employment_id: int) -> Optional[Employment]:
        rows = self.conn.execute(
            "SELECT start, end, company, supervisor, address, phone FROM employment WHERE id = ?",
            (employment_id,),
        ).fetchone()

        return self._map_row(row) if row else None

    def list(self) -> List[Employment]:
        rows = self.conn.execute(
            "SELECT start, end, company, supervisor, address, phone FROM employment"
        ).fetchall()

        return [self._map_row(row) for row in rows]

    def find(
        self,
        start: str = None,
        end: str = None,
        company: str = None,
        supervisor: str = None,
        address: str = None,
        phone: str = None,
    ) -> List[Employment]:
        query = "SELECT start, end, company, supervisor, address, phone FROM employment"
        conditions = []
        params = []

        if start:
            start_input = normalize_date(start)
            conditions.append("start = ?")
            params.append(start_input)

        if end:
            end_input = normalize_date(end_input)
            conditions.append("end = ?")
            params.append(end)

        if company:
            conditions.append("company = ?")
            params.append(company)

        if supervisor:
            conditions.append("supervisor = ?")
            params.append(supervisor)

        if address:
            conditions.append("address = ?")
            params.append(address)

        if phone:
            conditions.append("phone = ?")
            params.append(phone)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        rows = self.conn.execute(query, params).fetchall()
        return [self._map_row(row) for row in rows]

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
