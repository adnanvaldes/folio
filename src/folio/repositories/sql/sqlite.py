import sqlite3
from abc import abstractmethod
from typing import Optional, List, Any

from ..base import Repository
from folio.models import R
from folio.common import normalize_date


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

    @abstractmethod
    def _ensure_table(self) -> None: ...

    @abstractmethod
    def _map_row(self) -> R: ...

    def add(self, record: R) -> int:
        values = [getattr(record, field) for field in self.VALID_FIELDS]
        sql = f"INSERT INTO {self._table_name} ({self.columns}) VALUES ({self.placeholders})"
        cursor = self.conn.execute(sql, values)
        return cursor.lastrowid

    def get(self, id_: int) -> Optional[R]:
        sql = f"SELECT {self.columns} FROM {self._table_name} WHERE id = ?"
        row = self.conn.execute(sql, (id_,)).fetchone()
        return self._map_row(row) if row else None

    def find(self, **fields) -> List[R]:
        conditions = []
        params = []

        for field, value in self._filter_fields(fields).items():
            normalized_value = self._normalize_value(field, value)
            if normalized_value is not None:
                conditions.append(f"{field} = ?")
                params.append(normalized_value)

        sql = f"SELECT {self.columns} FROM {self._table_name}"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        rows = self.conn.execute(sql, params).fetchall()
        return [self._map_row(row) for row in rows]

    def list(self) -> List[R]:
        sql = f"SELECT {self.columns} FROM {self._table_name}"
        rows = self.conn.execute(sql).fetchall()
        return [self._map_row(row) for row in rows]

    def update(self, key: int, **field: dict[str, Any]) -> int:
        if not self.get(key):
            raise ValueError(f"Record with ID {key} not found")

        if not fields:
            raise ValueError("No fields provided")

        valid_updates = self._filter_fields(fields)
        if not valid_updates:
            raise ValueError(f"No valid fields passed with {fields}")

        set_clause = ", ".join(f"{field} = ?" for field in valid_updates)
        values = list(valid_updates.values()) + [key]

        sql = f"UPDATE {self._table_name} SET {update_fields} WHERE id = ?"
        cursor = self.conn.execute(sql, update_values)
        return cursor.rowcount

    def delete(self, key: int | None = None, **fields: dict[str, Any]) -> int:
        if key:
            sql = f"DELETE FROM {self._table_name} WHERE id = ?"
            cursor = self.conn.execute(sql, (key,))
            return cursor.rowcount

        where_clause = []
        values = []
        for field, value in self._filter_fields(fields).items():
            if value is not None:
                if field not in self.VALID_FIELDS:
                    raise ValueError(f"Invalid field:{field}")
                where_clause.append(f"{field} = ?")
                values.append(value)

        sql = f"DELETE FROM {self._table_name} WHERE {' AND '.join(where_clause)}"
        cursor = self.conn.execute(sql, values)
        return cursor.rowcount

    def _normalize_value(self, field: str, value: Any) -> Any:
        if value is None:
            return None
        if field in ("start", "end"):
            return normalize_date(value)
        if isinstance(value, str):
            return value.strip()
        return value

    def _filter_fields(self, fields: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in fields.items()
            if key in self.VALID_FIELDS and value is not None
        }
