from __future__ import annotations

from typing import Any

from .base import (
    AddressRepository,
    BookRepository,
    EducationRepository,
    EmploymentRepository,
    TravelRepository,
    WorkRepository,
)
from .sql.sqlite import (
    SQLiteAddressRepository,
    SQLiteBookRepository,
    SQLiteEducationRepository,
    SQLiteEmploymentRepository,
    SQLiteTravelRepository,
    SQLiteWorkRepository,
)

__all__ = [
    "AddressRepository",
    "BookRepository",
    "EducationRepository",
    "EmploymentRepository",
    "TravelRepository",
    "WorkRepository",
    "PgAddressRepository",
    "PgBookRepository",
    "PgEducationRepository",
    "PgEmploymentRepository",
    "PgTravelRepository",
    "PgWorkRepository",
    "SQLiteAddressRepository",
    "SQLiteBookRepository",
    "SQLiteEducationRepository",
    "SQLiteEmploymentRepository",
    "SQLiteTravelRepository",
    "SQLiteWorkRepository",
]


def __getattr__(name: str) -> Any:
    _pg_classes = {
        "PgAddressRepository",
        "PgBookRepository",
        "PgEducationRepository",
        "PgEmploymentRepository",
        "PgTravelRepository",
        "PgWorkRepository",
    }
    if name in _pg_classes:
        import importlib

        mod = importlib.import_module("folio.repositories.sql.postgres")
        return getattr(mod, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
