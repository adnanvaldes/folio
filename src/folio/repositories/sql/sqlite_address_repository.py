import sqlite3
import datetime as dt
from typing import Optional, List

from .sqlite import SQLiteRepository
from folio.models import Address
from folio.common import normalize_date


class SQLiteAddressRepository(SQLiteRepository[Address]):

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self._ensure_table()

    def add(self, address: Address) -> int:
        cursor = self.conn.execute(
            """INSERT INTO address (
            start,
            end,
            street,
            city,
            province,
            country,
            postal_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                address.start,
                address.end,
                address.street,
                address.city,
                address.province,
                address.country,
                address.postal_code,
            ),
        )

        return cursor.lastrowid

    def get(self, address_id: int) -> Optional[Address]:
        row = self.conn.execute(
            "SELECT start, end, street, city, province, country, postal_code FROM address WHERE id = ?",
            (address_id,),
        ).fetchone()

        return self._map_row(row) if row else None

    def list(self) -> List[Address]:
        rows = self.conn.execute(
            "SELECT start, end, street, city, province, country, postal_code FROM address"
        ).fetchall()

        return [self._map_row(row) for row in rows]

    def delete(self, key: int = None, **filters) -> int:
        if key:
            self.conn.execute("DELETE FROM address WHERE id = ?", (key,))
            return 1
        elif filters:
            where = []
            values = []
            for field, value in filters.items():
                if value is not None:
                    where.append(f"{field} = ?")
                    values.append(value)

            where_clause = " AND ".join(where)
            cursor = self.conn.execute(
                f"DELETE FROM address WHERE {where_clause}", values
            )
            return cursor.rowcount

    def find(
        self,
        start: str = None,
        end: str = None,
        street: str = None,
        city: str = None,
        province: str = None,
        country: str = None,
        postal_code: str = None,
    ) -> List[Address]:
        query = "SELECT start, end, street, city, province, country, postal_code FROM address"
        conditions = []
        params = []

        filters = {
            "street": street,
            "city": city,
            "country": country,
            "postal_code": postal_code,
            "start": normalize_date(start) if start else None,
            "end": normalize_date(end) if end else None,
            "province": province,
        }

        for field, value in filters.items():
            if value:
                conditions.append(f"{field} = ?")
                params.append(value.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        rows = self.conn.execute(query, params).fetchall()
        return [self._map_row(row) for row in rows]

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
            UNIQUE(street, city, province, country, postal_code, start, end)
        )
            """
        )
