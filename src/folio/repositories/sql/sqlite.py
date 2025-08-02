import sqlite3
from abc import abstractmethod
from typing import Optional, List

from ..base import Repository
from folio.models import R


class SQLiteRepository(Repository[R]):

    # Must be overriden in subclasses
    VALID_FIELDS: tuple[str, ...]
    RECORD_TYPE: type[R]

    def __init__(self, connection: sqlite3.Connection):
        if not hasattr(self, "RECORD_TYPE"):
            raise NotImplementedError(
                f"{self.__class__.__name__} must define RECORD_TYPE"
            )

        if not hasattr(self, "VALID_FIELDS"):
            raise NotImplementedError(
                f"{self.__class__.__name__} must define VALID_FIELDS"
            )

        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    @property
    def _table_name(self) -> str:
        return self.RECORD_TYPE.__name__.lower()

    @property
    def columns(self) -> str:
        return ", ".join(self.VALID_FIELDS)

    @property
    def placeholders(self) -> str:
        return ", ".join(["?"] * (len(self.VALID_FIELDS)))

    # @abstractmethod
    # def add(self, record: R) -> None: ...

    # @abstractmethod
    # def get(self, id: int) -> Optional[R]: ...

    @abstractmethod
    def _ensure_table(self) -> None: ...

    def add(self, record: R) -> int:
        values = [getattr(record, field) for field in self.VALID_FIELDS]
        cursor = self.conn.execute(
            f"INSERT INTO {self._table_name} ({self.columns}) VALUES ({self.placeholders})",
            values,
        )
        return cursor.lastrowid

    def get(self, id_: int) -> Optional[R]:
        row = self.conn.execute(
            f"SELECT {self.columns} FROM {self._table_name} WHERE id = ?",
            (id_,),
        ).fetchone()

        return self._map_row(row) if row else None

    def list(self) -> List[R]:
        rows = self.conn.execute(
            f"SELECT {self.columns} FROM {self._table_name}"
        ).fetchall()

        return [self._map_row(row) for row in rows]
