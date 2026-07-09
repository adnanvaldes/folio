import sqlite3
import datetime as dt
from typing import List

from folio.repositories import EmploymentRepository
from folio.models import Employment


class SQLiteEmploymentRepository(EmploymentRepository):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employment (
                company     TEXT NOT NULL,
                start       TEXT NOT NULL,
                end         TEXT,
                supervisor  TEXT NOT NULL,
                address     TEXT NOT NULL,
                phone       TEXT NOT NULL,
                CHECK(end IS NULL OR end >= start),
                UNIQUE(company, start)
            )
        """
        )

    def _map_row(self, row: sqlite3.Row) -> Employment:
        data = dict(row)
        data["start"] = dt.date.fromisoformat(data["start"])
        data["end"] = dt.date.fromisoformat(data["end"]) if data["end"] else None
        return Employment(**data)

    def _to_params(self, employment: Employment) -> dict:
        return {
            "company": employment.company,
            "start": employment.start.isoformat(),
            "end": employment.end.isoformat() if employment.end else None,
            "supervisor": employment.supervisor,
            "address": employment.address,
            "phone": employment.phone,
        }

    def _where_clause(self, params: dict) -> str:
        parts = []
        for field, value in params.items():
            if value is None:
                parts.append(f"{field} IS NULL")
            else:
                parts.append(f"{field} = :{field}")
        return " AND ".join(parts)

    def list(self) -> list[Employment]:
        rows = self.conn.execute(
            """
            SELECT company, start, end, supervisor, address, phone
            FROM employment
            ORDER BY start
        """
        ).fetchall()
        return [self._map_row(row) for row in rows]

    def add(self, employment: Employment) -> None:
        existing = self.find(
            company=employment.company,
            start=employment.start,
        )
        if existing:
            raise ValueError(f"Employment already exists: {employment}")
        params = self._to_params(employment)
        try:
            self.conn.execute(
                """
                INSERT INTO employment (company, start, end, supervisor, address, phone)
                VALUES (:company, :start, :end, :supervisor, :address, :phone)
            """,
                params,
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Employment already exists: {employment}")

    def remove(self, employment: Employment) -> None:
        params = self._to_params(employment)
        cursor = self.conn.execute(
            f"DELETE FROM employment WHERE {self._where_clause(params)}",
            {k: v for k, v in params.items() if v is not None},
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Employment not found: {employment}")

    def replace(self, old: Employment, new: Employment) -> None:
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
            f"UPDATE employment "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise ValueError(f"Employment not found: {old}")

    def find(self, **filters) -> List[Employment]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        if not filters:
            return self.list()

        conditions = []
        params = {}
        for field, value in filters.items():
            if value is None:
                conditions.append(f"{field} IS NULL")
            elif field == "company":
                conditions.append(f"LOWER({field}) = :{field}")
                params[field] = value.lower().strip()
            elif field in ("start", "end"):
                conditions.append(f"{field} = :{field}")
                params[field] = value.isoformat()
            else:
                conditions.append(f"{field} = :{field}")
                params[field] = value

        sql = (
            f"SELECT company, start, end, supervisor, address, phone "
            f"FROM employment WHERE {' AND '.join(conditions)} ORDER BY start"
        )
        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]

    def update(
        self,
        employment: Employment,
        *,
        end: dt.date | None = None,
        supervisor: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> None:
        if end is None and supervisor is None and address is None and phone is None:
            raise ValueError("No fields to update")

        updates = {}
        if end is not None:
            updates["end"] = end.isoformat()
        if supervisor is not None:
            updates["supervisor"] = supervisor.strip()
        if address is not None:
            updates["address"] = address.strip()
        if phone is not None:
            updates["phone"] = phone.strip()

        identity = self._to_params(employment)
        where_conditions = []
        where_params = {}
        for field, value in identity.items():
            if value is None:
                where_conditions.append(f"{field} IS NULL")
            else:
                where_params[f"where_{field}"] = value
                where_conditions.append(f"{field} = :where_{field}")

        set_clause = ", ".join(f"{f} = :set_{f}" for f in updates)
        set_params = {f"set_{k}": v for k, v in updates.items()}

        sql = (
            f"UPDATE employment SET {set_clause} WHERE {' AND '.join(where_conditions)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise ValueError(f"Employment not found: {employment}")
