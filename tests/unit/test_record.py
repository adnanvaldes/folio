import datetime as dt
import pytest
import json

from folio.models import (
    Work,
    Book,
    Travel,
    Address,
    Employment,
    FormatType,
    TextFormat,
    AudioFormat,
)


class TestWork:
    def test_work_creation(self, work_instance):
        work = work_instance

        assert work.title == "Abril Jacarandil"
        assert work.author == "Josu Roldan"
        assert work.year == 2024
        assert work.genre == "Poetry"
        assert work.is_read is False

    def test_work_identity_and_ordering(self, work_factory):
        w1 = work_factory(title="Alpha", author="Anderson", year=1990)
        w2 = work_factory(
            title="Alpha", author="Anderson", year=1990, genre="Sci-Fi"
        )  # Same identity
        w3 = work_factory(title="Beta", author="Anderson", year=1985)
        w4 = work_factory(title="Alpha", author="Brown", year=2000)

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
    def test_book_creation(self, book_instance):
        book = book_instance

        assert book.work.title == "Abril Jacarandil"
        assert book.work.author == "Josu Roldan"
        assert book.length == 127  # TextFormat pages
        assert book.format == FormatType.PRINT.value
        assert book.isbn == "9786079818180"

    def test_book_identity_and_ordering(self, book_factory, work_factory):
        work1 = work_factory(title="Alpha", author="Anderson", year=1990)
        work2 = work_factory(title="Beta", author="Brown", year=2000)

        # Same Work, same format, same ISBN -> same identity
        b1 = book_factory(
            work=work1,
            format_type=FormatType.AUDIO,
            duration=dt.timedelta(hours=10),
            narrator="John Smith",
            isbn="111",
        )
        b2 = book_factory(
            work=work1,
            format_type=FormatType.AUDIO,
            duration=dt.timedelta(hours=12),
            narrator="Jane Doe",
            isbn="111",
        )
        # Same Work and ISBN, different format
        b3 = book_factory(
            work=work1,
            format_type=FormatType.EBOOK,
            pages=300,
            isbn="111",
        )
        # Same Work, different ISBN
        b4 = book_factory(
            work=work1,
            format_type=FormatType.PRINT,
            pages=300,
            isbn="222",
        )
        # Different Work
        b5 = book_factory(
            work=work2,
            format_type=FormatType.PRINT,
            pages=300,
            isbn="111",
        )

        expected_order = [b1, b3, b4, b5]

        books = [b5, b3, b4, b1]
        assert sorted(books) == expected_order

        assert b1 == b2
        assert hash(b1) == hash(b2)
        for other in [b3, b4, b5]:
            assert b1 != other
            assert hash(b1) != hash(other)


class TestTravel:
    def test_travel_creation(self, travel_instance):
        travel = travel_instance

        assert travel.origin == "NYC"
        assert travel.destination == "LON"
        assert travel.date == dt.date(2020, 1, 1)
        assert travel.notes == "Vacation"

    def test_travel_identity_and_ordering(self, travel_factory):
        t1 = travel_factory(origin="NYC", destination="LON", date=dt.date(2020, 1, 1))
        # Same identity
        t2 = travel_factory(
            origin="NYC", destination="LON", date=dt.date(2020, 1, 1), notes="Business"
        )
        # Diff identity
        t3 = travel_factory(origin="PAR", destination="ROM", date=dt.date(2021, 1, 1))

        expected_order = [t1, t3]
        travels = [t3, t1]
        assert sorted(travels) == expected_order

        # Identity
        assert t1 == t2
        assert hash(t1) == hash(t2)
        assert t1 != t3
        assert hash(t1) != hash(t3)


class TestAddress:
    def test_address_creation(self, address_instance):
        addr = address_instance

        assert addr.start == dt.date(2020, 1, 1)
        assert addr.end is None
        assert addr.street_address == "123 Main"
        assert addr.province == "ON"
        assert addr.country == "Canada"
        assert addr.postal_code == "A1B2C3"
        assert isinstance(addr.duration, timedelta)

    def test_address_identity_and_ordering(self, address_factory):
        a1 = address_factory(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 1, 1),
            street_address="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a2 = address_factory(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 1, 1),
            street_address="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a3 = address_factory(
            start=dt.date(2021, 6, 1),
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
    def test_employment_creation(self, employment_instance):
        emp = employment_instance

        assert emp.start == dt.date(2020, 1, 1)
        assert emp.end is None
        assert emp.company == "Acme"
        assert emp.supervisor == "Wild E. Coyote"
        assert emp.address == "123 Some St"
        assert emp.phone == "555-1234"

    def test_employment_identity_and_ordering(self, employment_factory):
        e1 = employment_factory(start=dt.date(2025, 1, 1), company="Acme")
        e2 = employment_factory(start=dt.date(1900, 2, 2), company="Acme")
        e3 = employment_factory(
            start=dt.date(2020, 1, 1),
            end=dt.date(2025, 1, 1),
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
