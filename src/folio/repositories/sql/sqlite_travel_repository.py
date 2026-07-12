import datetime as dt
import sqlite3

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Travel
from folio.repositories import TravelRepository
from folio.repositories.sql._filters import (
    build_where_clause,
    parse_filter_key,
    validate_filter_fields,
)


class SQLiteTravelRepository(TravelRepository):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS travel (
                origin      TEXT NOT NULL,
                destination TEXT NOT NULL,
                date        TEXT NOT NULL,
                note       TEXT,
                CHECK(length(origin) = 3 AND origin = UPPER(origin)),
                CHECK(length(destination) = 3 AND destination = UPPER(destination)),
                UNIQUE(origin, destination, date)
            )
        """)

    def _map_row(self, row: sqlite3.Row) -> Travel:
        data = dict(row)
        data["date"] = dt.date.fromisoformat(data["date"])
        return Travel(**data)

    def _to_params(self, travel: Travel) -> dict:
        return {
            "origin": travel.origin,
            "destination": travel.destination,
            "date": travel.date.isoformat(),
            "note": travel.note,
        }

    def list_all(self) -> list[Travel]:
        rows = self.conn.execute("""
            SELECT origin, destination, date, note
            FROM travel
            ORDER BY date
        """).fetchall()
        return [self._map_row(row) for row in rows]

    def add(self, travel: Travel) -> None:
        existing = self.find(
            origin=travel.origin,
            destination=travel.destination,
            date=travel.date,
        )
        if existing:
            raise FolioDuplicateError(f"Travel already exists: {travel}")
        params = self._to_params(travel)
        try:
            self.conn.execute(
                """
                INSERT INTO travel (origin, destination, date, note)
                VALUES (:origin, :destination, :date, :note)
            """,
                params,
            )
        except sqlite3.IntegrityError:
            raise FolioDuplicateError(f"Travel already exists: {travel}")

    def remove(self, travel: Travel) -> None:
        params = self._to_params(travel)
        cursor = self.conn.execute(
            f"DELETE FROM travel WHERE {build_where_clause(params)}",
            {k: v for k, v in params.items() if v is not None},
        )
        if cursor.rowcount == 0:
            raise FolioNotFoundError(f"Travel not found: {travel}")

    def replace(self, old: Travel, new: Travel) -> None:
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
            f"UPDATE travel "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise FolioNotFoundError(f"Travel not found: {old}")

    def find(self, **filters) -> list[Travel]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

        case_insensitive_fields = {"origin", "destination"}

        conditions = []
        params = {}
        for key, value in filters.items():
            field, op = parse_filter_key(key)
            if op == "contains":
                conditions.append(f"LOWER({field}) LIKE :{key}")
                params[key] = f"%{value.lower().strip()}%"
            elif op == "before":
                conditions.append(f"{field} < :{key}")
                params[key] = value.isoformat()
            elif op == "after":
                conditions.append(f"{field} > :{key}")
                params[key] = value.isoformat()
            elif value is None:
                conditions.append(f"{field} IS NULL")
            elif field in case_insensitive_fields:
                conditions.append(f"LOWER({field}) = :{field}")
                params[field] = value.lower().strip()
            elif field == "date":
                params[field] = value.isoformat()
                conditions.append(f"{field} = :{field}")
            else:
                params[field] = value
                conditions.append(f"{field} = :{field}")

        sql = (
            f"SELECT origin, destination, date, note "
            f"FROM travel WHERE {' AND '.join(conditions)} ORDER BY date"
        )
        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]
