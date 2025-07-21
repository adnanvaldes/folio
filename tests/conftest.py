import pytest
import datetime as dt

from tests.data import DEFAULTS, WORKS, BOOKS, TRAVELS, ADDRESSES, EMPLOYMENTS
from folio.models import Work, Book, Travel, Address, Employment


@pytest.fixture
def work_instance() -> Work:
    return Work(**DEFAULTS.WORK)


@pytest.fixture
def book_instance(work_instance) -> Book:
    return Book(work=work_instance, **DEFAULTS.BOOK)


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
        work=None, pages=100, format=Book.Format.PRINT, isbn="9783161484100"
    ):
        if work is None:
            work = work_factory()
        return Book(work, pages, format, isbn)

    return _create_book


@pytest.fixture
def travel_factory():
    """Factory for creating Travel instances with custom parameters"""

    def _create_travel(
        origin="NYC", destination="LON", date=dt.date(2020, 1, 1), notes="Travel"
    ):
        return Travel(origin=origin, destination=destination, date=dt.date, notes=notes)

    return _create_travel


@pytest.fixture
def address_factory():
    """Factory for creating Address instances with custom parameters"""

    def _create_address(
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 1, 1),
        street_address="123 Main St",
        province="ON",
        country="Canada",
        postal_code="A1B2C3",
    ):
        return Address(
            start=start,
            end=end,
            street_address=street_address,
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


@pytest.fixture(params=list(zip(WORKS, BOOKS)))
def multiple_books(request) -> Book:
    """Parametrized fixture that creates multiple Book instances with associated Works"""
    work_data, book_data = request.param
    work = Work(**work_data)
    return Book(work=work, **book_data)


@pytest.fixture(params=TRAVELS)
def multiple_travels(request) -> Travel:
    return Travel(**request.param)


@pytest.fixture(params=ADDRESSES)
def multiple_addresses(request) -> Address:
    return Address(**request.param)


@pytest.fixture(params=EMPLOYMENTS)
def multiple_employments(request) -> Employment:
    return Employment(**request.params)


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
