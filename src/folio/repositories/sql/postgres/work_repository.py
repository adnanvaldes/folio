import psycopg

from folio.exceptions import (
    FolioDuplicateError,
    FolioNotFoundError,
    FolioValidationError,
)
from folio.models import Work
from folio.repositories import WorkRepository
from folio.repositories.sql import (
    build_where_clause,
    parse_filter_key,
    validate_filter_fields,
)


def _work_identity_where(
    author: str, title: str, year: int | None
) -> tuple[str, dict[str, str | int]]:
    """Build WHERE clause and params for matching a Work by identity.

    Returns (where_clause, params) where params contains lowered/stripped
    values for author and title. Used by both PgWorkRepository and
    PgBookRepository so identity logic stays in one place.
    """
    params: dict[str, str | int] = {
        "author": author.lower().strip(),
        "title": title.lower().strip(),
    }
    if year is None:
        return (
            "LOWER(author) = %(author)s AND LOWER(title) = %(title)s AND year IS NULL",
            params,
        )
    params["year"] = year
    return (
        "LOWER(author) = %(author)s AND LOWER(title) = %(title)s AND year = %(year)s",
        params,
    )


class PgWorkRepository(WorkRepository):

    def __init__(self, connection: psycopg.Connection):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS work (
                    id          SERIAL PRIMARY KEY,
                    author      TEXT NOT NULL,
                    title       TEXT NOT NULL,
                    year        INTEGER,
                    genre       TEXT,
                    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
                    UNIQUE(author, title, year)
                )
            """)

    def _map_row(self, row) -> Work:
        return Work(**row)

    def _to_params(self, work: Work) -> dict:
        return {
            "author": work.author,
            "title": work.title,
            "year": work.year,
            "genre": work.genre,
            "is_read": work.is_read,
        }

    def list_all(self) -> list[Work]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT author, title, year, genre, is_read
                FROM work
                ORDER BY LOWER(author), LOWER(title), year
            """)
            return [self._map_row(row) for row in cur.fetchall()]

    def add(self, work: Work) -> None:
        existing = self.find(
            author=work.author,
            title=work.title,
            year=work.year,
        )
        if existing:
            raise FolioDuplicateError(f"Work already exists: {work}")
        params = self._to_params(work)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO work (author, title, year, genre, is_read)
                    VALUES (%(author)s, %(title)s, %(year)s, %(genre)s, %(is_read)s)
                """,
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Work already exists: {work}")

    def remove(self, work: Work) -> None:
        params = self._to_params(work)
        filtered = {k: v for k, v in params.items() if v is not None}
        where = build_where_clause(filtered, placeholder="%({field})s")
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM work WHERE {where}",
                filtered,
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Work not found: {work}")

    def replace(self, old: Work, new: Work) -> None:
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
            f"UPDATE work "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Work not found: {old}")

    def find(self, **filters) -> list[Work]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

        conditions = []
        params: dict = {}

        identity_keys = {"author", "title", "year"}

        def _build_condition(key: str, value) -> tuple[str, dict]:
            field, op = parse_filter_key(key)
            if op == "contains":
                return (
                    f"LOWER({field}) LIKE %({key})s",
                    {key: f"%{value.lower().strip()}%"},
                )
            if op in ("before", "after"):
                sym = "<" if op == "before" else ">"
                return (
                    f"{field} {sym} %({key})s",
                    {key: value},
                )
            if value is None:
                return (f"{field} IS NULL", {})
            if field in ("author", "title"):
                return (
                    f"LOWER({field}) = %({field})s",
                    {field: value.lower().strip()},
                )
            return (f"{field} = %({field})s", {field: value})

        id_filters = {
            k: v for k, v in filters.items() if parse_filter_key(k)[0] in identity_keys
        }
        non_id_filters = {
            k: v
            for k, v in filters.items()
            if parse_filter_key(k)[0] not in identity_keys
        }

        all_id_exact = all(parse_filter_key(k)[1] is None for k in id_filters)
        if len(id_filters) == 3 and all_id_exact:
            where, id_params = _work_identity_where(**id_filters)
            conditions.append(where)
            params.update(id_params)
        else:
            for key, value in id_filters.items():
                cond, p = _build_condition(key, value)
                conditions.append(cond)
                params.update(p)

        for key, value in non_id_filters.items():
            cond, p = _build_condition(key, value)
            conditions.append(cond)
            params.update(p)

        sql = (
            f"SELECT author, title, year, genre, is_read "
            f"FROM work WHERE {' AND '.join(conditions)} "
            f"ORDER BY LOWER(author), LOWER(title), year"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        if genre is None and is_read is None:
            raise FolioValidationError("No fields to update")

        updates: dict[str, str | bool] = {}
        if genre is not None:
            updates["genre"] = genre
        if is_read is not None:
            updates["is_read"] = is_read

        identity_fields = {"author", "title", "year"}
        params = self._to_params(work)
        where_conditions = []
        where_params = {}
        for field in identity_fields:
            value = params[field]
            if value is None:
                where_conditions.append(f"{field} IS NULL")
            else:
                where_params[f"where_{field}"] = value
                where_conditions.append(f"{field} = %(where_{field})s")

        set_clause = ", ".join(f"{f} = %(set_{f})s" for f in updates)
        set_params = {f"set_{k}": v for k, v in updates.items()}

        sql = f"UPDATE work SET {set_clause} WHERE {' AND '.join(where_conditions)}"

        with self.conn.cursor() as cur:
            cur.execute(sql, {**where_params, **set_params})
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Work not found: {work}")
