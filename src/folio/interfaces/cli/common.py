import datetime as dt

from folio.exceptions import (
    FolioAmbiguousQueryError,
    FolioNotFoundError,
    FolioParseError,
)

from .config import resolve_backend


def parse_date(s):
    if s is None:
        return None
    return dt.date.fromisoformat(s)


def parse_bool(s):
    if s.lower() in ("yes", "true", "1", "y"):
        return True
    if s.lower() in ("no", "false", "0", "n"):
        return False
    raise FolioParseError(f"Invalid boolean: '{s}' (expected yes/no/true/false/1/0)")


def find_one(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise FolioNotFoundError("Record not found")
    if len(results) > 1:
        raise FolioAmbiguousQueryError(f"Expected one record, found {len(results)}")
    return results[0]


_UOWS: dict = {}


def _load_uows(db_url):
    if _UOWS:
        return
    if resolve_backend(db_url) == "postgres":
        from folio.uow.postgres.postgres_uow import (
            AddressPostgresUoW,
            BookPostgresUoW,
            EducationPostgresUoW,
            EmploymentPostgresUoW,
            TravelPostgresUoW,
            WorkPostgresUoW,
        )

        _UOWS.update(
            address=AddressPostgresUoW,
            book=BookPostgresUoW,
            education=EducationPostgresUoW,
            employment=EmploymentPostgresUoW,
            travel=TravelPostgresUoW,
            work=WorkPostgresUoW,
        )
    else:
        from folio.uow import (
            AddressSQLiteUoW,
            BookSQLiteUoW,
            EducationSQLiteUoW,
            EmploymentSQLiteUoW,
            TravelSQLiteUoW,
            WorkSQLiteUoW,
        )

        _UOWS.update(
            address=AddressSQLiteUoW,
            book=BookSQLiteUoW,
            education=EducationSQLiteUoW,
            employment=EmploymentSQLiteUoW,
            travel=TravelSQLiteUoW,
            work=WorkSQLiteUoW,
        )


def make_travel_uow(db_url):
    _load_uows(db_url)
    return _UOWS["travel"](db_url)


def make_address_uow(db_url):
    _load_uows(db_url)
    return _UOWS["address"](db_url)


def make_education_uow(db_url):
    _load_uows(db_url)
    return _UOWS["education"](db_url)


def make_employment_uow(db_url):
    _load_uows(db_url)
    return _UOWS["employment"](db_url)


def make_work_uow(db_url):
    _load_uows(db_url)
    return _UOWS["work"](db_url)


def make_book_uow(db_url):
    _load_uows(db_url)
    return _UOWS["book"](db_url)
