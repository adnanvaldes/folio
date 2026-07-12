import datetime as dt

import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Employment


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    from folio.repositories import PgEmploymentRepository
    return PgEmploymentRepository(pg_conn)


def make_employment(**overrides) -> Employment:
    defaults = dict(
        company="Acme Corp",
        start=dt.date(2020, 1, 1),
        end=None,
        supervisor="John Boss",
        address="123 Work Ave",
        phone="555-1234",
    )
    return Employment(**{**defaults, **overrides})


class TestPgEmploymentRepositoryAdd:

    def test_add_and_list(self, repo):
        e = make_employment()
        repo.add(e)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == e

    def test_add_duplicate_raises(self, repo):
        e = make_employment()
        repo.add(e)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(e)


class TestPgEmploymentRepositoryRemove:

    def test_remove_existing(self, repo):
        e = make_employment()
        repo.add(e)
        repo.remove(e)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_employment())


class TestPgEmploymentRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_employment(supervisor="Wrong")
        repo.add(original)
        corrected = make_employment(supervisor="Corrected")
        repo.replace(original, corrected)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0].supervisor == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        e1 = make_employment(company="A", start=dt.date(2020, 1, 1))
        e2 = make_employment(company="B", start=dt.date(2021, 1, 1))
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.replace(e1, e2)


class TestPgEmploymentRepositoryUpdate:

    def test_update_supervisor(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, supervisor="New Boss")
        result = repo.list_all()[0]
        assert result.supervisor == "New Boss"

    def test_update_end(self, repo):
        e = make_employment()
        repo.add(e)
        repo.update(e, end=dt.date(2023, 12, 31))
        result = repo.list_all()[0]
        assert result.end == dt.date(2023, 12, 31)

    def test_update_no_fields_raises(self, repo):
        from folio.exceptions import FolioValidationError

        e = make_employment()
        repo.add(e)
        with pytest.raises(FolioValidationError, match="No fields to update"):
            repo.update(e)

    def test_update_nonexistent_raises(self, repo):
        e = make_employment()
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.update(e, supervisor="X")


class TestPgEmploymentRepositoryFind:

    def test_find_by_company(self, repo):
        e1 = make_employment(company="Acme")
        e2 = make_employment(company="Globex", start=dt.date(2021, 1, 1))
        repo.add(e1)
        repo.add(e2)
        results = repo.find(company="Acme")
        assert len(results) == 1
        assert results[0].company == "Acme"

    def test_find_by_company_case_insensitive(self, repo):
        e = make_employment(company="Acme")
        repo.add(e)
        results = repo.find(company="acme")
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        e1 = make_employment(company="A")
        e2 = make_employment(company="B", start=dt.date(2021, 1, 1))
        repo.add(e1)
        repo.add(e2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")
