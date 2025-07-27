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
        assert work_instance.title == "Abril Jacarandil"
        assert work_instance.author == "Josu Roldan"
        assert work_instance.year == 2024
        assert work_instance.genre == "Poetry"
        assert work_instance.is_read is False

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
        assert book_instance.work.title == "Abril Jacarandil"
        assert book_instance.work.author == "Josu Roldan"
        assert book_instance.length == 127  # TextFormat pages
        assert book_instance.format == FormatType.PRINT.value
        assert book_instance.isbn == "9786079818180"

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
        assert travel_instance.origin == "NYC"
        assert travel_instance.destination == "LON"
        assert travel_instance.date == dt.date(2020, 1, 1)
        assert travel_instance.notes == "Vacation"

    def test_travel_rejects_non_dates(self, travel_factory):
        with pytest.raises(TypeError):
            travel_factory(date="string")

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
        assert address_instance.start == dt.date(2020, 1, 1)
        assert address_instance.end is None
        assert address_instance.street == "123 Main"
        assert address_instance.province == "ON"
        assert address_instance.country == "Canada"
        assert address_instance.postal_code == "A1B2C3"
        assert isinstance(address_instance.duration, dt.timedelta)

    def test_address_rejects_non_dates(self, address_factory):
        with pytest.raises(TypeError):
            address_factory(start="not a date")

        with pytest.raises(TypeError):
            address_factory(end="not a date")

    def test_address_rejects_end_before_start(self, address_factory):
        with pytest.raises(ValueError):
            address_factory(start=dt.date(2000, 1, 1), end=dt.date(1000, 1, 1))

    def test_address_duration(self, address_factory):
        address = address_factory(start=dt.date(1000, 1, 1), end=dt.date(1000, 1, 31))
        assert address.duration == dt.timedelta(days=30)

    def test_address_identity_and_ordering(self, address_factory):
        a1 = address_factory(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 1, 1),
            street="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a2 = address_factory(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 1, 1),
            street="123 Main St",
            province="ON",
            country="Canada",
            postal_code="A1B2C3",
        )
        a3 = address_factory(
            start=dt.date(2021, 6, 1),
            end=None,
            street="456 Elm St",
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
    def test_employment_creation(self, employment_instance, employment_factory):
        e1 = employment_factory(start=dt.date(1000, 1, 1), end=dt.date(1000, 1, 1))

        assert employment_instance.start == dt.date(2020, 1, 1)
        assert employment_instance.end is None
        assert employment_instance.company == "Acme"
        assert employment_instance.supervisor == "Wild E. Coyote"
        assert employment_instance.address == "123 Some St"
        assert employment_instance.phone == "555-1234"

    def test_employment_rejects_non_dates(self, employment_factory):
        with pytest.raises(TypeError):
            employment_factory(start="a string")

        with pytest.raises(TypeError):
            employment_factory(end="a string")

    def test_employment_rejects_end_before_start(self, employment_factory):
        with pytest.raises(ValueError):
            employment_factory(start=dt.date(2000, 1, 1), end=dt.date(1000, 1, 1))

    def test_employment_duration(self, employment_factory):
        employment = employment_factory(
            start=dt.date(1000, 1, 1), end=dt.date(1000, 1, 31)
        )
        assert employment.duration == dt.timedelta(days=30)

    def test_employment_identity_and_ordering(self, employment_factory):
        e1 = employment_factory(start=dt.date(2025, 1, 1), company="Acme")
        e2 = employment_factory(
            start=dt.date(2025, 1, 1), company="Acme", end=dt.date(2026, 1, 1)
        )

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
