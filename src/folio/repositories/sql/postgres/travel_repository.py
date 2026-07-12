import psycopg

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Travel
from folio.repositories import TravelRepository
from folio.repositories.sql import (
    build_where_clause,
    parse_filter_key,
    validate_filter_fields,
)


class PgTravelRepository(TravelRepository):

    def __init__(self, connection: psycopg.Connection):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS travel (
                    origin      VARCHAR(3) NOT NULL,
                    destination VARCHAR(3) NOT NULL,
                    date        DATE NOT NULL,
                    note        TEXT,
                    CHECK (origin = UPPER(origin)),
                    CHECK (destination = UPPER(destination)),
                    UNIQUE(origin, destination, date)
                )
            """)

    def _map_row(self, row) -> Travel:
        return Travel(**row)

    def _to_params(self, travel: Travel) -> dict:
        return {
            "origin": travel.origin,
            "destination": travel.destination,
            "date": travel.date,
            "note": travel.note,
        }

    def list_all(self) -> list[Travel]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT origin, destination, date, note
                FROM travel
                ORDER BY date
            """)
            return [self._map_row(row) for row in cur.fetchall()]

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
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO travel (origin, destination, date, note)
                    VALUES (%(origin)s, %(destination)s, %(date)s, %(note)s)
                """,
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Travel already exists: {travel}")

    def remove(self, travel: Travel) -> None:
        params = self._to_params(travel)
        filtered = {k: v for k, v in params.items() if v is not None}
        where = build_where_clause(filtered, placeholder="%({field})s")
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM travel WHERE {where}",
                filtered,
            )
            if cur.rowcount == 0:
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
                where_parts.append(f"{field} = %(old_{field})s")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{field} = %(new_{field})s")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE travel "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
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
                conditions.append(f"LOWER({field}) LIKE %({key})s")
                params[key] = f"%{value.lower().strip()}%"
            elif op == "before":
                conditions.append(f"{field} < %({key})s")
                params[key] = value
            elif op == "after":
                conditions.append(f"{field} > %({key})s")
                params[key] = value
            elif value is None:
                conditions.append(f"{field} IS NULL")
            elif field in case_insensitive_fields:
                conditions.append(f"{field} ILIKE %({field})s")
                params[field] = value.strip()
            elif field == "date":
                params[field] = value
                conditions.append(f"{field} = %({field})s")
            else:
                params[field] = value
                conditions.append(f"{field} = %({field})s")

        sql = (
            f"SELECT origin, destination, date, note "
            f"FROM travel WHERE {' AND '.join(conditions)} ORDER BY date"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]
