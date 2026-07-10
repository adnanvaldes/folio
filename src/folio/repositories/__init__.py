from .base import (
    AddressRepository,
    BookRepository,
    EducationRepository,
    EmploymentRepository,
    TravelRepository,
    WorkRepository,
)
from .sql.sqlite_address_repository import SQLiteAddressRepository
from .sql.sqlite_book_repository import SQLiteBookRepository
from .sql.sqlite_education_repository import SQLiteEducationRepository
from .sql.sqlite_employment_repository import SQLiteEmploymentRepository
from .sql.sqlite_travel_repository import SQLiteTravelRepository
from .sql.sqlite_work_repository import SQLiteWorkRepository

__all__ = [
    "AddressRepository",
    "EducationRepository",
    "TravelRepository",
    "WorkRepository",
    "EmploymentRepository",
    "BookRepository",
    "SQLiteTravelRepository",
    "SQLiteEducationRepository",
    "SQLiteEmploymentRepository",
    "SQLiteAddressRepository",
    "SQLiteWorkRepository",
    "SQLiteBookRepository",
]
