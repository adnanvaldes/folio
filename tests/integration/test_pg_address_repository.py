import datetime as dt

import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Address


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    from folio.repositories import PgAddressRepository

    return PgAddressRepository(pg_conn)


def make_address(**overrides) -> Address:
    defaults = dict(
        street="123 Main St",
        city="Springfield",
        country="USA",
        postal_code="62704",
        start=dt.date(2020, 1, 1),
        end=None,
        province="IL",
    )
    return Address(**{**defaults, **overrides})


class TestPgAddressRepositoryAdd:

    def test_add_and_list(self, repo):
        a = make_address()
        repo.add(a)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == a

    def test_add_duplicate_raises(self, repo):
        a = make_address()
        repo.add(a)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(a)


class TestPgAddressRepositoryRemove:

    def test_remove_existing(self, repo):
        a = make_address()
        repo.add(a)
        repo.remove(a)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_address())


class TestPgAddressRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_address(city="Wrong")
        repo.add(original)
        corrected = make_address(city="Corrected")
        repo.replace(original, corrected)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0].city == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        a1 = make_address(street="1 Old St", city="A", start=dt.date(2020, 1, 1))
        a2 = make_address(street="2 New St", city="B", start=dt.date(2021, 1, 1))
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.replace(a1, a2)


class TestPgAddressRepositoryFind:

    def test_find_by_city(self, repo):
        a1 = make_address(city="Springfield")
        a2 = make_address(city="Shelbyville", start=dt.date(2021, 1, 1))
        repo.add(a1)
        repo.add(a2)
        results = repo.find(city="Springfield")
        assert len(results) == 1
        assert results[0].city == "Springfield"

    def test_find_by_city_case_insensitive(self, repo):
        a = make_address(city="Springfield")
        repo.add(a)
        results = repo.find(city="springfield")
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        a1 = make_address(city="A")
        a2 = make_address(city="B", start=dt.date(2021, 1, 1))
        repo.add(a1)
        repo.add(a2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")
