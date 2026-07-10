import datetime as dt
import sqlite3

import pytest

from folio.models import Employment
from folio.repositories import SQLiteEmploymentRepository


@pytest.fixture
def repo(fake_db):
    conn = sqlite3.connect(fake_db)
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN")
    repo = SQLiteEmploymentRepository(conn)
    yield repo
    conn.close()


def make_employment(**overrides) -> Employment:
    defaults = dict(
        company="Acme Corp",
        start=dt.date(2024, 1, 1),
        supervisor="Jane Doe",
        address="123 Main St",
        phone="555-0100",
        end=None,
    )
    return Employment(**{**defaults, **overrides})


class TestSQLiteEmploymentRepositoryAdd:

    def test_add_and_list(self, repo):
        e = make_employment()
        repo.add(e)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == e

    def test_add_duplicate_raises(self, repo):
        e = make_employment()
        repo.add(e)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(e)

    def test_add_duplicate_case_insensitive_raises(self, repo):
        e1 = make_employment(company="Acme Corp")
        e2 = make_employment(company="acme corp")
        repo.add(e1)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(e2)

    def test_list_returns_chronological_order(self, repo):
        e1 = make_employment(start=dt.date(2024, 6, 1))
        e2 = make_employment(start=dt.date(2024, 1, 1))
        e3 = make_employment(start=dt.date(2024, 3, 1))
        repo.add(e1)
        repo.add(e2)
        repo.add(e3)
        assert repo.list_all() == [e2, e3, e1]

    def test_same_company_different_start_allowed(self, repo):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(start=dt.date(2025, 1, 1))
        repo.add(e1)
        repo.add(e2)
        assert len(repo.list_all()) == 2


class TestSQLiteEmploymentRepositoryDates:

    def test_date_round_trips_as_date_object(self, repo):
        e = make_employment()
        repo.add(e)
        result = repo.list_all()[0]
        assert isinstance(result.start, dt.date)
        assert result.start == dt.date(2024, 1, 1)

    def test_end_date_round_trips(self, repo):
        e = make_employment(end=dt.date(2024, 12, 31))
        repo.add(e)
        result = repo.list_all()[0]
        assert isinstance(result.end, dt.date)
        assert result.end == dt.date(2024, 12, 31)

    def test_none_end_round_trips(self, repo):
        e = make_employment(end=None)
        repo.add(e)
        result = repo.list_all()[0]
        assert result.end is None


class TestSQLiteEmploymentRepositoryRemove:

    def test_remove_existing(self, repo):
        e = make_employment()
        repo.add(e)
        repo.remove(e)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(ValueError, match="not found"):
            repo.remove(make_employment())


class TestSQLiteEmploymentRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_employment(supervisor="Wrong")
        repo.add(original)

        corrected = make_employment(supervisor="Corrected")
        repo.replace(original, corrected)

        result = repo.list_all()
        assert len(result) == 1
        assert result[0].supervisor == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        original = make_employment()
        other = make_employment(company="Other Corp")
        with pytest.raises(ValueError, match="not found"):
            repo.replace(original, other)


class TestSQLiteEmploymentRepositoryFind:

    def test_find_by_company(self, repo):
        e1 = make_employment()
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        repo.add(e1)
        repo.add(e2)

        results = repo.find(company="Acme Corp")
        assert len(results) == 1
        assert results[0].company == "Acme Corp"

    def test_find_by_company_case_insensitive(self, repo):
        e = make_employment(company="Acme Corp")
        repo.add(e)
        results = repo.find(company="acme corp")
        assert len(results) == 1

    def test_find_by_start(self, repo):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        repo.add(e1)
        repo.add(e2)

        results = repo.find(start=dt.date(2024, 1, 1))
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        repo.add(e1)
        repo.add(e2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            repo.find(invalid="x")


class TestSQLiteEmploymentRepositoryUpdate:

    def test_update_supervisor(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, supervisor="New Sup")
        result = repo.list_all()[0]
        assert result.supervisor == "New Sup"

    def test_update_end(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, end=dt.date(2024, 12, 31))
        result = repo.list_all()[0]
        assert result.end == dt.date(2024, 12, 31)

    def test_update_address(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, address="456 Oak")
        result = repo.list_all()[0]
        assert result.address == "456 Oak"

    def test_update_phone(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, phone="555-9999")
        result = repo.list_all()[0]
        assert result.phone == "555-9999"

    def test_update_no_fields_raises(self, repo):
        e = make_employment()
        repo.add(e)
        with pytest.raises(ValueError, match="No fields to update"):
            repo.update(e)

    def test_update_nonexistent_raises(self, repo):
        with pytest.raises(ValueError, match="not found"):
            repo.update(make_employment(), supervisor="New")
