from .base import Repository, BookRepository

from .sql.sqlite_travel_repository import SQLiteTravelRepository
from .sql.sqlite_employment_repository import SQLiteEmploymentRepository
from .sql.sqlite_address_repository import SQLiteAddressRepository
from .sql.sqlite_work_repository import SQLiteWorkRepository
from .sql.sqlite_book_repository import SQLiteBookRepository
from .sql.sqlite import SQLiteRepository


__all__ = [
    "Repository",
    "BookRepository",
    "SQLiteRepository",
    "SQLiteTravelRepository",
    "SQLiteEmploymentRepository",
    "SQLiteAddressRepository",
    "SQLiteWorkRepository",
    "SQLiteBookRepository",
]
