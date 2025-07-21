import sqlite3
from abc import abstractmethod
from typing import Optional

from ..base import Repository
from folio.models import R


class SQLiteRepository(Repository[R]):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

    @abstractmethod
    def add(self, record: R) -> None: ...

    @abstractmethod
    def get(self, id: int) -> Optional[R]: ...

    @abstractmethod
    def _ensure_table(self) -> None: ...
