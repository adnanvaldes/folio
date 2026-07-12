from .base import (
    AddressRepository,
    BookRepository,
    EducationRepository,
    EmploymentRepository,
    TravelRepository,
    WorkRepository,
)
from .sql.postgres import (
    PgAddressRepository,
    PgBookRepository,
    PgEducationRepository,
    PgEmploymentRepository,
    PgTravelRepository,
    PgWorkRepository,
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
    "EducationRepository",
    "TravelRepository",
    "WorkRepository",
    "EmploymentRepository",
    "BookRepository",
    "PgTravelRepository",
    "PgEducationRepository",
    "PgEmploymentRepository",
    "PgAddressRepository",
    "PgWorkRepository",
    "PgBookRepository",
    "SQLiteTravelRepository",
    "SQLiteEducationRepository",
    "SQLiteEmploymentRepository",
    "SQLiteAddressRepository",
    "SQLiteWorkRepository",
    "SQLiteBookRepository",
]
