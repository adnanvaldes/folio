import sqlite3
from typing import List

from folio.models import Work
from folio.repositories import WorkRepository


class SQLiteWorkRepository(WorkRepository):

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS work (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                author      TEXT NOT NULL,
                title       TEXT NOT NULL,
                year        INTEGER,
                genre       TEXT,
                is_read     INTEGER NOT NULL CHECK(is_read IN (0,1)),
                UNIQUE(author, title, year)
            )
        """)

    def _map_row(self, row: sqlite3.Row) -> Work:
        data = dict(row)
        data["is_read"] = bool(data["is_read"])
        return Work(**data)

    def _to_params(self, work: Work) -> dict:
        return {
            "author": work.author,
            "title": work.title,
            "year": work.year,
            "genre": work.genre,
            "is_read": int(work.is_read),
        }

    def _where_clause(self, params: dict) -> str:
        parts = []
        for field, value in params.items():
            if value is None:
                parts.append(f"{field} IS NULL")
            else:
                parts.append(f"{field} = :{field}")
        return " AND ".join(parts)

    def list(self) -> List[Work]:
        rows = self.conn.execute("""
            SELECT author, title, year, genre, is_read
            FROM work
            ORDER BY LOWER(author), LOWER(title), year
        """).fetchall()
        return [self._map_row(row) for row in rows]

    def add(self, work: Work) -> None:
        existing = self.find(
            author=work.author,
            title=work.title,
            year=work.year,
        )
        if existing:
            raise ValueError(f"Work already exists: {work}")
        params = self._to_params(work)
        try:
            self.conn.execute(
                """
                INSERT INTO work (author, title, year, genre, is_read)
                VALUES (:author, :title, :year, :genre, :is_read)
            """,
                params,
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Work already exists: {work}")

    def remove(self, work: Work) -> None:
        params = self._to_params(work)
        cursor = self.conn.execute(
            f"DELETE FROM work WHERE {self._where_clause(params)}",
            {k: v for k, v in params.items() if v is not None},
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Work not found: {work}")

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
                where_parts.append(f"{field} = :old_{field}")

        set_parts = []
        set_params = {}
        for field, value in new_params.items():
            set_parts.append(f"{field} = :new_{field}")
            set_params[f"new_{field}"] = value

        sql = (
            f"UPDATE work "
            f"SET {', '.join(set_parts)} "
            f"WHERE {' AND '.join(where_parts)}"
        )

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise ValueError(f"Work not found: {old}")

    def find(self, **filters) -> List[Work]:
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
            elif field in ("author", "title"):
                conditions.append(f"LOWER({field}) = :{field}")
                params[field] = value.lower().strip()
            else:
                conditions.append(f"{field} = :{field}")
                params[field] = value

        sql = (
            f"SELECT author, title, year, genre, is_read "
            f"FROM work WHERE {' AND '.join(conditions)} "
            f"ORDER BY LOWER(author), LOWER(title), year"
        )
        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        if genre is None and is_read is None:
            raise ValueError("No fields to update")

        updates: dict[str, str | int] = {}
        if genre is not None:
            updates["genre"] = genre
        if is_read is not None:
            updates["is_read"] = int(is_read)

        identity = self._to_params(work)
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

        sql = f"UPDATE work SET {set_clause} WHERE {' AND '.join(where_conditions)}"

        cursor = self.conn.execute(sql, {**where_params, **set_params})
        if cursor.rowcount == 0:
            raise ValueError(f"Work not found: {work}")
