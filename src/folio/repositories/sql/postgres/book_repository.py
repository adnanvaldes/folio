import psycopg
from psycopg.rows import DictRow

from folio.exceptions import FolioDuplicateError, FolioNotFoundError
from folio.models import Book, FormatType, Work
from folio.repositories import BookRepository
from folio.repositories.sql import parse_filter_key, validate_filter_fields

from .work_repository import _work_identity_where


class PgBookRepository(BookRepository):

    def __init__(self, connection: psycopg.Connection[DictRow]):
        self.conn = connection
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS book ("
                "    work_id          INTEGER NOT NULL REFERENCES work(id),"
                "    format_type      TEXT NOT NULL,"
                "    isbn             TEXT,"
                "    pages            INTEGER,"
                "    duration_minutes INTEGER,"
                "    narrator         TEXT,"
                "    UNIQUE(work_id, format_type, isbn)"
                ")"
            )

    def _map_row(self, row) -> Book:
        work = Work(
            author=row["author"],
            title=row["title"],
            year=row["year"],
            genre=row["genre"],
            is_read=row["is_read"],
        )
        return Book(
            work=work,
            format_type=FormatType(row["format_type"]),
            isbn=row["isbn"],
            pages=row["pages"],
            duration_minutes=row["duration_minutes"],
            narrator=row["narrator"],
        )

    def _to_params(self, book: Book) -> dict:
        return {
            "work_id": self._lookup_work_id(book.work),
            "format_type": book.format_type.value,
            "isbn": book.isbn,
            "pages": book.pages,
            "duration_minutes": book.duration_minutes,
            "narrator": book.narrator,
        }

    def _lookup_work_id(self, work: Work) -> int:
        where, params = _work_identity_where(work.author, work.title, work.year)
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT id FROM work WHERE {where}", params)
            row = cur.fetchone()
        if row is None:
            raise FolioNotFoundError(f"Referenced work does not exist: {work}")
        return row["id"]

    def _join_select(self) -> str:
        return (
            "SELECT b.work_id, b.format_type, b.isbn,"
            "       b.pages, b.duration_minutes, b.narrator,"
            "       w.author, w.title, w.year, w.genre, w.is_read"
            " FROM book b"
            " JOIN work w ON w.id = b.work_id"
        )

    def list_all(self) -> list[Book]:
        with self.conn.cursor() as cur:
            cur.execute(
                f"{self._join_select()}"
                " ORDER BY LOWER(w.author), LOWER(w.title), w.year,"
                "          b.format_type, b.isbn"
            )
            return [self._map_row(row) for row in cur.fetchall()]

    def add(self, book: Book) -> None:
        existing = self.find(
            author=book.work.author,
            title=book.work.title,
            year=book.work.year,
            format_type=book.format_type,
            isbn=book.isbn,
        )
        if existing:
            raise FolioDuplicateError(f"Book already exists: {book}")
        params = self._to_params(book)
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO book (work_id, format_type, isbn,"
                    "                  pages, duration_minutes, narrator)"
                    " VALUES (%(work_id)s, %(format_type)s, %(isbn)s,"
                    "         %(pages)s, %(duration_minutes)s, %(narrator)s)",
                    params,
                )
        except psycopg.IntegrityError:
            raise FolioDuplicateError(f"Book already exists: {book}")

    def remove(self, book: Book) -> None:
        params = self._to_params(book)
        isbn_clause = "isbn IS NULL" if book.isbn is None else "isbn = %(isbn)s"
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM book WHERE work_id = %(work_id)s"
                f" AND format_type = %(format_type)s"
                f" AND {isbn_clause}",
                params,
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Book not found: {book}")

    def replace(self, old: Book, new: Book) -> None:
        old_params = self._to_params(old)
        new_params = self._to_params(new)

        isbn_clause = "isbn IS NULL" if old.isbn is None else "isbn = %(old_isbn)s"

        with self.conn.cursor() as cur:
            cur.execute(
                f"UPDATE book SET"
                f"    work_id = %(new_work_id)s,"
                f"    format_type = %(new_format_type)s,"
                f"    isbn = %(new_isbn)s,"
                f"    pages = %(new_pages)s,"
                f"    duration_minutes = %(new_duration_minutes)s,"
                f"    narrator = %(new_narrator)s"
                f" WHERE work_id = %(old_work_id)s"
                f" AND format_type = %(old_format_type)s"
                f" AND {isbn_clause}",
                {
                    "old_work_id": old_params["work_id"],
                    "old_format_type": old_params["format_type"],
                    **({} if old.isbn is None else {"old_isbn": old_params["isbn"]}),
                    "new_work_id": new_params["work_id"],
                    "new_format_type": new_params["format_type"],
                    "new_isbn": new_params["isbn"],
                    "new_pages": new_params["pages"],
                    "new_duration_minutes": new_params["duration_minutes"],
                    "new_narrator": new_params["narrator"],
                },
            )
            if cur.rowcount == 0:
                raise FolioNotFoundError(f"Book not found: {old}")

    def find(self, **filters) -> list[Book]:
        validate_filter_fields(filters, self.VALID_FIELDS)

        if not filters:
            return self.list_all()

        work_fields = {"author", "title", "year"}
        conditions = []
        params = {}
        for key, value in filters.items():
            field, op = parse_filter_key(key)
            prefix = "w." if field in work_fields else "b."
            if op == "contains":
                conditions.append(f"LOWER({prefix}{field}) LIKE %({key})s")
                params[key] = f"%{value.lower().strip()}%"
            elif op in ("before", "after"):
                sym = "<" if op == "before" else ">"
                conditions.append(f"{prefix}{field} {sym} %({key})s")
                params[key] = value
            elif value is None:
                conditions.append(f"{prefix}{field} IS NULL")
            elif field in ("author", "title"):
                conditions.append(f"LOWER({prefix}{field}) = %({field})s")
                params[field] = value.lower().strip()
            elif field == "year":
                conditions.append(f"{prefix}{field} = %({field})s")
                params[field] = value
            elif field == "format_type":
                conditions.append(f"{prefix}{field} = %({field})s")
                params[field] = value.value if isinstance(value, FormatType) else value
            else:
                conditions.append(f"{prefix}{field} = %({field})s")
                params[field] = value

        sql = (
            f"{self._join_select()} WHERE {' AND '.join(conditions)} "
            f"ORDER BY LOWER(w.author), LOWER(w.title), w.year, "
            f"b.format_type, b.isbn"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return [self._map_row(row) for row in cur.fetchall()]
