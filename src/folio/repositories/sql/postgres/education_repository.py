import psycopg

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Education
from folio.repositories import EducationRepository
from folio.repositories.sql import (
    build_where_clause,
    col,
    parse_filter_key,
    validate_filter_fields,
)


class PgEducationRepository(EducationRepository):

    def __init__(self, connection: psycopg.Connection):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS education ("
                "    field        TEXT NOT NULL,"
                "    start        DATE NOT NULL,"
                '    "end"        DATE NOT NULL,'
                "    school       TEXT NOT NULL,"
                "    city         TEXT NOT NULL,"
                "    country      TEXT NOT NULL,"
                "    credential   TEXT NOT NULL,"
                '    CHECK("end" >= start),'
                '    UNIQUE(field, start, "end", school, city, country, credential)'
                ")"
            )

    def _map_row(self, row) -> Education:
        return Education(**row)

    def _to_params(self, education: Education) -> dict:
        return {
            "field": education.field,
            "start": education.start,
            "end": education.end,
            "school": education.school,
            "city": education.city,
            "country": education.country,
            "credential": education.credential,
        }

    def list_all(self) -> list[Education]:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT field, start, {col('end')}, school, city, country, credential"
                " FROM education ORDER BY start"
            )
            return [self._map_row(row) for row in cur.fetchall()]

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
            with self.conn.cursor() as cur:
                cur.execute(
                    f"INSERT INTO education"
                    f" (field, start, {col('end')}, school, city, country, credential)"
                    " VALUES (%(field)s, %(start)s, %(end)s,"
                    "         %(school)s, %(city)s, %(country)s, %(credential)s)",
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Education already exists: {education}")

    def remove(self, education: Education) -> None:
        params = self._to_params(education)
        where = build_where_clause(params, placeholder="%({field})s")
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM education WHERE {where}",
                params,
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Education not found: {education}")

    def replace(self, old: Education, new: Education) -> None:
        old_params = self._to_params(old)
        new_params = self._to_params(new)

        where_parts = []
        where_params = {}
        for field, value in old_params.items():
            where_params[f"old_{field}"] = value
            where_parts.append(f"{col(field)} = %(old_{field})s")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{col(field)} = %(new_{field})s")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE education "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
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
                conditions.append(f"LOWER({col(field)}) LIKE %({key})s")
                params[key] = f"%{value.lower().strip()}%"
            elif op == "before":
                conditions.append(f"{col(field)} < %({key})s")
                params[key] = value
            elif op == "after":
                conditions.append(f"{col(field)} > %({key})s")
                params[key] = value
            elif value is None:
                conditions.append(f"{col(field)} IS NULL")
            elif field in case_insensitive_fields:
                conditions.append(f"{col(field)} ILIKE %({field})s")
                params[field] = value.strip()
            elif field in ("start", "end"):
                conditions.append(f"{col(field)} = %({field})s")
                params[field] = value
            else:
                conditions.append(f"{col(field)} = %({field})s")
                params[field] = value

        sql = (
            f"SELECT field, start, {col('end')}, school, city, country, credential"
            " FROM education WHERE"
            f" {' AND '.join(conditions)} ORDER BY start"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]
