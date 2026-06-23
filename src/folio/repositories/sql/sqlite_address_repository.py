import sqlite3
import datetime as dt

from folio.repositories.base import AddressRepository
from folio.models import Address

class SQLiteAddressRepository(AddressRepository):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn,row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS address (
                street      TEXT NOT NULL,
                city        TEXT NOT NULL,
                province    TEXT,
                country     TEXT NOT NULL,
                postal_code TEXT NOT NULL,
                start       TEXT,
                end         TEXT,
                CHECK(end IS NULL OR end > start),
                UNIQUE(street, city, country, postal_code, province, start, end)
            )
        """)

    def _map_row(self, row: sqlite3.Row) -> Address:
        data = dict(row)
        data["start"] = dt.date.fromisoformat(data["start"])
        data["end"] = dt.date.fromisoformat(data["end"] if data["end"] else None)
        return Address(**data)

    def _to_params(self, address: Address) -> dict:
        return {
            "street":      address.street,
            "city":        address.city,
            "country":     address.country,
            "postal_code": address.postal_code,
            "province":    address.province,
            "start":       address.start.isoformat(),
            "end":         address.end.isoformat() if address.end else None,
        }

    def _where_clause(self, params: dict) -> str:
        """
        Build a WHERE clause that handles NULL values.
        """
        parts = []
        for field, value in params.items():
            if value is None:
                parts.append(f"{field} IS NULL")
            else:
                parts.append(f"{field} = :{field}")
        return " AND ".join(parts)

    def list(self) -> list[Address]:
        rows = self.conn.execute("""
            SELECT start, end, street, city, province, country, postal_code
            FROM address
            ORDER BY start
        """).fetchall()
        return [self._map_row(row) for row in rows]

    def add(self, address: Address) -> None:
        params = self._to_params(address)
        try:
            self.conn.execute("""
                INSERT INTO address
                    (street, city, country, postal_code, province, start, end)
                VALUES
                    (:street, :city, :country, :postal_code, :province, :start, :end)
            """, params)
        except sqlite3.IntegrityError:
            raise ValueError(f"Address already exist: {address}")

    def remove(self, address: Address) -> None:
        params = self._to_params(address)
        cursor = self.conn.execute(
            f"DELETE FROM address WHERE {self._where_clause(params)}",
            {k: v for k,v in params.items() if v is not None}
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Address not found: {address}")

    def replace(self, old: Address, new: Address) -> None:
        old_params = self._to_params(old)
        new_params = self._to_params(new)

        where_parts = []
        where_params = {}
        for field, value in old_params.items():
            if value is None:
                where_parts.append(f"{field} IS NULL")
            else:
                where_params[f"old_{field}"] = value
                where_parts.append(f"{field} = :old_{field}")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{field} = :new_{field}")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE address "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise ValueError(f"Address not found: {old}")

    def find(self, **filters) -> list[Address]:
        invalid = set(filters) - self.VALID_FILTERS
        if invalid:
            raise ValueError(f"Invalid filters: {invalid}")

        if not filters:
            return self.list()

        params = {}
        conditions = []

        for field, value in filters.items():
            if value is None:
                conditions.append(f"{field} IS NULL")
            else:
                if field in ("start", "end"):
                    value = value.isoformat()

                conditions.append(f"{field} = :{field}")
                params[field] = value

        sql = (
            f"SELECT start, end, street, city, province, country, postal_code "
            f"FROM address WHERE {' AND '.join(conditions)} ORDER BY start"
        )
        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]
