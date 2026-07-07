import datetime as dt
import pytest
import sqlite3
from folio.models.address import Address
from folio.repositories.sql.sqlite_address_repository import SQLiteAddressRepository


@pytest.fixture
def repo(fake_db):
    """
    A repository connected to a fresh SQLite database.
    We test the repository directly here — no service, no UoW.
    This lets us verify SQL behaviour in isolation.
    """
    conn = sqlite3.connect(fake_db)
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN")
    return SQLiteAddressRepository(conn)


def make_address(**overrides) -> Address:
    defaults = dict(
        street="123 Main St",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 12, 31),
    )
    return Address(**{**defaults, **overrides})


class TestSQLiteAddressRepositoryAdd:

    def test_add_and_list(self, repo):
        addr = make_address()
        repo.add(addr)
        assert addr in repo.list()

    def test_add_duplicate_raises(self, repo):
        addr = make_address()
        repo.add(addr)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(addr)

    def test_list_returns_chronological_order(self, repo):
        a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        b = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
        )
        repo.add(b)
        repo.add(a)
        result = repo.list()
        assert result == [a, b]


class TestSQLiteAddressRepositoryDates:

    def test_start_date_round_trips_as_date_object(self, repo):
        """
        Verifies we never use the deprecated implicit date adapter.
        dt.date must survive SQLite as dt.date, not string.
        """
        addr = make_address(start=dt.date(2020, 1, 1))
        repo.add(addr)
        retrieved = repo.list()[0]
        assert isinstance(retrieved.start, dt.date)
        assert retrieved.start == dt.date(2020, 1, 1)

    def test_end_date_round_trips_as_date_object(self, repo):
        addr = make_address(end=dt.date(2022, 12, 31))
        repo.add(addr)
        retrieved = repo.list()[0]
        assert isinstance(retrieved.end, dt.date)
        assert retrieved.end == dt.date(2022, 12, 31)

    def test_open_address_end_is_none_not_string(self, repo):
        """
        end=None must come back as None, not as the string "None"
        or any other representation.
        """
        addr = make_address(end=None)
        repo.add(addr)
        retrieved = repo.list()[0]
        assert retrieved.end is None


class TestSQLiteAddressRepositoryNullHandling:

    def test_find_open_addresses_uses_is_null(self, repo):
        """
        find(end=None) must generate IS NULL in SQL, not = NULL.
        = NULL never matches anything in SQL — this test catches that bug.
        """
        closed = make_address(end=dt.date(2022, 12, 31))
        open_addr = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        repo.add(closed)
        repo.add(open_addr)

        results = repo.find(end=None)
        assert len(results) == 1
        assert results[0] == open_addr

    def test_province_none_round_trips_as_none(self, repo):
        """
        province=None must survive SQLite as None.
        A common bug is NULL coming back as "" or missing.
        """
        addr = make_address(province=None)
        repo.add(addr)
        retrieved = repo.list()[0]
        assert retrieved.province is None

    def test_province_value_round_trips_correctly(self, repo):
        addr = make_address(province="BC")
        repo.add(addr)
        retrieved = repo.list()[0]
        assert retrieved.province == "BC"


class TestSQLiteAddressRepositoryRemove:

    def test_remove_existing_address(self, repo):
        addr = make_address()
        repo.add(addr)
        repo.remove(addr)
        assert addr not in repo.list()

    def test_remove_nonexistent_raises(self, repo):
        addr = make_address()
        with pytest.raises(ValueError, match="not found"):
            repo.remove(addr)

    def test_remove_open_address_uses_is_null(self, repo):
        """
        Removing an open address requires IS NULL in the WHERE clause.
        WHERE end = NULL never matches — this test catches that bug.
        """
        addr = make_address(end=None)
        repo.add(addr)
        repo.remove(addr)
        assert repo.list() == []


class TestSQLiteAddressRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_address(street="123 Main St")
        repo.add(original)

        corrected = make_address(street="123 Main Street")
        repo.replace(original, corrected)

        result = repo.list()
        assert len(result) == 1
        assert result[0].street == "123 Main Street"

    def test_replace_nonexistent_raises(self, repo):
        original = make_address()
        corrected = make_address(street="456 Elm St")
        with pytest.raises(ValueError, match="not found"):
            repo.replace(original, corrected)

    def test_replace_open_address_uses_is_null(self, repo):
        """
        Replacing an open address requires IS NULL in the WHERE clause.
        """
        open_addr = make_address(end=None)
        repo.add(open_addr)

        closed = make_address(end=dt.date(2022, 12, 31))
        repo.replace(open_addr, closed)

        result = repo.list()
        assert result[0].end == dt.date(2022, 12, 31)


class TestSQLiteAddressRepositoryFind:

    def test_find_by_city(self, repo):
        a = make_address(city="Vancouver")
        b = make_address(
            street="456 Elm St",
            city="Toronto",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        repo.add(a)
        repo.add(b)

        results = repo.find(city="Vancouver")
        assert len(results) == 1
        assert results[0].city == "Vancouver"

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            repo.find(nonexistent="value")
