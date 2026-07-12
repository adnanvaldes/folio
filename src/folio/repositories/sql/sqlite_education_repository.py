import datetime as dt
import sqlite3

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Education
from folio.repositories import EducationRepository
from folio.repositories.sql._filters import (
    build_where_clause,
    parse_filter_key,
    validate_filter_fields,
)


class SQLiteEducationRepository(EducationRepository):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS education (
                field        TEXT NOT NULL,
                start        TEXT NOT NULL,
                end          TEXT NOT NULL,
                school       TEXT NOT NULL,
                city         TEXT NOT NULL,
                country      TEXT NOT NULL,
                credential   TEXT NOT NULL,
                CHECK(end >= start),
                UNIQUE(field, start, end, school, city, country, credential)
            )
        """)

    def _map_row(self, row: sqlite3.Row) -> Education:
        data = dict(row)
        data["start"] = dt.date.fromisoformat(data["start"])
        data["end"] = dt.date.fromisoformat(data["end"])
        return Education(**data)

    def _to_params(self, education: Education) -> dict:
        return {
            "field": education.field,
            "start": education.start.isoformat(),
            "end": education.end.isoformat(),
            "school": education.school,
            "city": education.city,
            "country": education.country,
            "credential": education.credential,
        }

    def list_all(self) -> list[Education]:
        rows = self.conn.execute("""
            SELECT field, start, end, school, city, country, credential
            FROM education
            ORDER BY start
        """).fetchall()
        return [self._map_row(row) for row in rows]

    def add(self, education: Education) -> None:
        existing = self.find(
            field=education.field,
            start=education.start,
            end=education.end,
            school=education.school,
            city=education.city,
            country=education.country,
            credential=education.credential,
        )
        if existing:
            raise FolioDuplicateError(f"Education already exists: {education}")
        params = self._to_params(education)
        try:
            self.conn.execute(
                """
                INSERT INTO education
                    (field, start, end, school, city, country, credential)
                VALUES
                    (:field, :start, :end, :school, :city, :country, :credential)
            """,
                params,
            )
        except sqlite3.IntegrityError:
            raise FolioDuplicateError(f"Education already exists: {education}")

    def remove(self, education: Education) -> None:
        params = self._to_params(education)
        cursor = self.conn.execute(
            f"DELETE FROM education WHERE {build_where_clause(params)}",
            params,
        )
        if cursor.rowcount == 0:
            raise FolioNotFoundError(f"Education not found: {education}")

    def replace(self, old: Education, new: Education) -> None:
        old_params = self._to_params(old)
        new_params = self._to_params(new)

        where_parts = []
        where_params = {}
        for field, value in old_params.items():
            where_params[f"old_{field}"] = value
            where_parts.append(f"{field} = :old_{field}")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{field} = :new_{field}")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE education "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise FolioNotFoundError(f"Education not found: {old}")

    def find(self, **filters) -> list[Education]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

        case_insensitive_fields = {"field", "school", "city", "country", "credential"}

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
            elif field in ("start", "end"):
                conditions.append(f"{field} = :{field}")
                params[field] = value.isoformat()
            else:
                conditions.append(f"{field} = :{field}")
                params[field] = value

        sql = (
            f"SELECT field, start, end, school, city, country, credential "
            f"FROM education WHERE {' AND '.join(conditions)} ORDER BY start"
        )
        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]
