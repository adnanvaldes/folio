import pytest
import json
from datetime import date, timedelta

from folio.models.models import Work, Book, Travel, Address, Employment


def work_instance(
    title="Default Title",
    author="Default Author",
    year=2020,
    genre="Fiction",
    is_read=False,
) -> Work:
    return Work(title, author, year, genre, is_read)


def book_instance(
    work: Work | None = None,
    pages: int | None = 100,
    format=Book.Format.PRINT,
    isbn: str | None = "9783161484100",
) -> Book:
    return Book(work or work_instance(), pages, format, isbn)


def travel_instance(
    origin="NYC", destination="LON", date=date(2020, 1, 1), notes="Vacation"
) -> Travel:
    return Travel(origin=origin, destination=destination, date=date, notes=notes)


def employment_instance(
    start=date(2020, 1, 1),
    end=None,
    company="Acme",
    supervisor="Wild E. Coyote",
    address="123 Some St",
    phone="555-1234",
) -> Employment:
    return Employment(
        start=start,
        end=end,
        company=company,
        supervisor=supervisor,
        address=address,
        phone=phone,
    )


def address_instance(
    start=date(2020, 1, 1),
    end=None,
    street_address="123 Main",
    province="ON",
    country="Canada",
    postal_code="A1B2C3",
) -> Address:
    return Address(
        start=start,
        end=end,
        street_address=street_address,
        province=province,
        country=country,
        postal_code=postal_code,
    )


class TestWork:
    def test_work_creation(self):
        work = work_instance(
            title="Test Book",
            author="Test Author",
            year=None,
            genre=None,
            is_read=False,
        )

        assert work.title == "Test Book"
        assert work.author == "Test Author"
        assert work.year is None
        assert work.genre is None
        assert work.is_read is False

    def test_work_identity_and_ordering(self):
        w1 = work_instance(title="Alpha", author="Anderson", year=1990)
        w2 = work_instance(
            title="Alpha", author="Anderson", year=1990, genre="Sci-Fi"
        )  # Same identity
        w3 = work_instance(title="Beta", author="Anderson", year=1985)
        w4 = work_instance(title="Alpha", author="Brown", year=2000)

        expected_order = [w1, w3, w4]

        # Ordering
        works = [w4, w3, w1]
        assert sorted(works) == expected_order

        # Identity
        assert w1 == w2
        assert hash(w1) == hash(w2)
        for other in [w3, w4]:
            assert w1 != other
            assert hash(w1) != hash(other)


class TestBook:
    def test_book_creation(self):
        work = work_instance()
        book = book_instance(work)

        assert book.work.title == "Default Title"
        assert book.work.author == "Default Author"
        assert book.pages == 100
        assert book.format == Book.Format.PRINT
        assert book.isbn == "9783161484100"

    def test_book_identity_and_ordering(self):
        work1 = work_instance(title="Alpha", author="Anderson", year=1990)
        work2 = work_instance(title="Beta", author="Brown", year=2000)

        b1 = book_instance(work=work1, format=Book.Format.AUDIO, isbn="111", pages=300)
        b2 = book_instance(
            work=work1, format=Book.Format.AUDIO, isbn="111", pages=400
        )  # Same identity
        b3 = book_instance(
            work=work1, format=Book.Format.EBOOK, isbn="111", pages=300
        )  # Diff format
        b4 = book_instance(
            work=work1, format=Book.Format.PRINT, isbn="222", pages=300
        )  # Diff ISBN
        b5 = book_instance(
            work=work2, format=Book.Format.PRINT, isbn="111", pages=300
        )  # Diff Work

        expected_order = [b1, b3, b4, b5]

        # Ordering
        books = [b5, b3, b4, b1]
        assert sorted(books) == expected_order

        # Identity
        assert b1 == b2
        assert hash(b1) == hash(b2)
        for other in [b3, b4, b5]:
            assert b1 != other
            assert hash(b1) != hash(other)


class TestTravel:
    def test_travel_creation(self):
        travel = travel_instance(
            origin="NYC", destination="LON", date=date(2020, 1, 1), notes="Vacation"
        )

        assert travel.origin == "NYC"
        assert travel.destination == "LON"
        assert travel.date == date(2020, 1, 1)
        assert travel.notes == "Vacation"

    def test_travel_identity_and_ordering(self):
        t1 = travel_instance(origin="NYC", destination="LON", date=date(2020, 1, 1))
        t2 = travel_instance(
            origin="NYC", destination="LON", date=date(2020, 1, 1), notes="Business"
        )  # Same identity
        t3 = travel_instance(
            origin="PAR", destination="ROM", date=date(2021, 1, 1)
        )  # Diff identity

        expected_order = [t1, t3]

        # Ordering
        travels = [t3, t1]
        assert sorted(travels) == expected_order

        # Identity
        assert t1 == t2
        assert hash(t1) == hash(t2)
        assert t1 != t3
        assert hash(t1) != hash(t3)


class TestAddress:
    def test_address_creation(self):
        addr = address_instance(
            start=date(2020, 1, 1),
            end=None,
            street_address="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )

        assert addr.start == date(2020, 1, 1)
        assert addr.end is None
        assert addr.street_address == "123 Main St"
        assert addr.province == "ON"
        assert addr.country == "Canada"
        assert addr.postal_code == "A1B2C3"
        assert isinstance(addr.duration, timedelta)

    def test_address_identity_and_ordering(self):
        a1 = address_instance(
            start=date(2020, 1, 1),
            end=date(2022, 1, 1),
            street_address="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a2 = address_instance(
            start=date(2018, 1, 1),
            end=date(2019, 1, 1),
            street_address="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a3 = address_instance(
            start=date(2021, 6, 1),
            end=None,
            street_address="456 Elm St",
            province="BC",
            country="Canada",
            postal_code="X9Y8Z7",
        )

        # Identity
        assert a1 == a2  # location matches, dates don't matter for identity
        assert hash(a1) == hash(a2)
        assert a1 != a3
        assert hash(a1) != hash(a3)

        # Ordering
        addresses = [a1, a3, a2]
        sorted_addresses = sorted(addresses)
        assert sorted_addresses == [a3, a2, a1]


class TestEmployment:
    def test_employment_creation(self):
        emp = employment_instance(
            start=date(2020, 1, 1),
            end=None,
            company="Acme",
            supervisor="Wild E. Coyote",
            address="123 Some St",
            phone="555-1234",
        )

        assert emp.start == date(2020, 1, 1)
        assert emp.end is None
        assert emp.company == "Acme"
        assert emp.supervisor == "Wild E. Coyote"
        assert emp.address == "123 Some St"
        assert emp.phone == "555-1234"

    def test_employment_identity_and_ordering(self):
        e1 = employment_instance(start=date(2025, 1, 1), company="Acme")
        e2 = employment_instance(start=date(1900, 2, 2), company="Acme")
        e3 = employment_instance(
            start=date(2020, 1, 1),
            end=date(2025, 1, 1),
            company="Megacorp",
            supervisor="Super Boss",
            address="789 Some Blvd",
            phone="555-9012",
        )

        # Ordering
        employments = [e1, e3]
        assert sorted(employments) == [e3, e1]

        # Identity
        assert e1 == e2
        assert hash(e1) == hash(e2)
        assert e1 != e3
        assert hash(e1) != hash(e3)
