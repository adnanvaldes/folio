import pytest
import sqlite3
import tempfile
import os
import datetime as dt
from typing import Optional, List, Dict


from folio.models import (
    Work,
    Book,
    Travel,
    Address,
    Employment,
    TextFormat,
    AudioFormat,
    FormatType,
    R,
)
from folio.uow import UnitOfWork

from tests.data import DEFAULTS, WORKS, BOOKS, TRAVELS, ADDRESSES, EMPLOYMENTS
import tests.fake_repositories as fake


class FakeUnitOfWork(UnitOfWork):
    def __init__(self):
        self.travel = fake.FakeTravelRepository()
        self.employment = fake.FakeEmploymentRepository()
        self.committed = False

    def _start(self):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

    def _cleanup(self):
        pass


@pytest.fixture
def fake_db():
    """Creates a temp SQLite DB file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.remove(path)


@pytest.fixture
def fake_uow():
    uow = FakeUnitOfWork()
    uow._start()
    return uow


@pytest.fixture
def fake_travel_repo():
    return fake.FakeTravelRepository()


@pytest.fixture
def fake_employment_repo():
    return fake.FakeEmploymentRepository()


# Model instances


@pytest.fixture
def work_instance() -> Work:
    return Work(**DEFAULTS.WORK)


@pytest.fixture
def book_instance(work_instance) -> Book:
    text_format = TextFormat(
        pages=DEFAULTS.TEXT_FORMAT["pages"],
        format_type=DEFAULTS.TEXT_FORMAT["format_type"],
    )
    return Book(
        work=work_instance,
        format_data=text_format,
        isbn=DEFAULTS.BOOK["isbn"],
    )


@pytest.fixture
def travel_instance() -> Travel:
    return Travel(**DEFAULTS.TRAVEL)


@pytest.fixture
def employment_instance() -> Employment:
    return Employment(**DEFAULTS.EMPLOYMENT)


@pytest.fixture
def address_instance() -> Address:
    return Address(**DEFAULTS.ADDRESS)


@pytest.fixture
def sample_records(
    work_instance, book_instance, travel_instance, employment_instance, address_instance
):
    """Fixture with one of each Record type"""
    return [
        work_instance,
        book_instance,
        travel_instance,
        employment_instance,
        address_instance,
    ]


@pytest.fixture
def work_factory():
    """Factory for creating Work instances with custom parameters"""

    def _create_work(
        title="Default Title",
        author="Default Author",
        year=2020,
        genre="Fiction",
        is_read=False,
    ):
        return Work(title, author, year, genre, is_read)

    return _create_work


@pytest.fixture
def book_factory(work_factory):
    """Factory for creating Book instances with custom parameters"""

    def _create_book(
        work=None,
        pages: int | None = 300,
        duration: dt.timedelta | None = None,
        format_type: FormatType = FormatType.PRINT,
        narrator: str | None = None,
        isbn="9783161484100",
    ):
        if work is None:
            work = work_factory()

        if format_type == FormatType.AUDIO:
            format_data = AudioFormat(
                duration=duration or dt.timedelta(hours=10),
                narrator=narrator,
            )
        else:
            format_data = TextFormat(
                pages=pages,
                format_type=format_type,
            )

        return Book(work=work, format_data=format_data, isbn=isbn)

    return _create_book


@pytest.fixture
def travel_factory():
    """Factory for creating Travel instances with custom parameters"""

    def _create_travel(
        origin="NYC", destination="LON", date=dt.date(2020, 1, 1), notes="Travel"
    ):
        return Travel(origin=origin, destination=destination, date=date, notes=notes)

    return _create_travel


@pytest.fixture
def address_factory():
    """Factory for creating Address instances with custom parameters"""

    def _create_address(
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 1, 1),
        street="123 Main St",
        city="Vancouver",
        province="ON",
        country="Canada",
        postal_code="A1B2C3",
    ):
        return Address(
            start=start,
            end=end,
            street=street,
            city=city,
            province=province,
            country=country,
            postal_code=postal_code,
        )

    return _create_address


@pytest.fixture
def employment_factory():
    """Factory for creating Employment instances with custom parameters"""

    def _create_employment(
        start=dt.date(2020, 1, 1),
        end=None,
        company="Acme",
        supervisor="Wild E. Coyote",
        address="123 Some St",
        phone="555-1234",
    ):
        return Employment(
            start=start,
            end=end,
            company=company,
            supervisor=supervisor,
            address=address,
            phone=phone,
        )

    return _create_employment


# Parametrized fixtures with multiple instances
@pytest.fixture(params=WORKS)
def multiple_works(request) -> Work:
    return Work(**request.param)


@pytest.fixture(params=BOOKS)
def multiple_books(request) -> Book:
    """Parametrized fixture that creates multiple Book instances with associated Works"""
    book_data = request.param
    return Book(
        work=book_data["work"],
        format_data=book_data["format_data"],
        isbn=book_data["isbn"],
    )


@pytest.fixture(params=TRAVELS)
def multiple_travels(request) -> Travel:
    return request.param


@pytest.fixture(params=ADDRESSES)
def multiple_addresses(request) -> Address:
    return Address(**request.param)


@pytest.fixture(params=EMPLOYMENTS)
def multiple_employments(request) -> Employment:
    return request.param


# Utility fixtures
@pytest.fixture
def past_date():
    """A date in the past"""
    return dt.date(2020, 1, 1)


@pytest.fixture
def future_date():
    """A date in the future"""
    return dt.date.today() + dt.timedelta(days=365)


@pytest.fixture
def date_range(past_date, future_date):
    """A tuple of (start_date, end_date)"""
    return (past_date, future_date)
