import datetime as dt

import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Education
from folio.repositories import PgEducationRepository


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    return PgEducationRepository(pg_conn)


def make_education(**overrides) -> Education:
    defaults = dict(
        field="Computer Science",
        start=dt.date(2016, 9, 1),
        end=dt.date(2020, 6, 15),
        school="MIT",
        city="Cambridge",
        country="USA",
        credential="Bachelor",
    )
    return Education(**{**defaults, **overrides})


class TestPgEducationRepositoryAdd:

    def test_add_and_list(self, repo):
        e = make_education()
        repo.add(e)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == e

    def test_add_duplicate_raises(self, repo):
        e = make_education()
        repo.add(e)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(e)


class TestPgEducationRepositoryRemove:

    def test_remove_existing(self, repo):
        e = make_education()
        repo.add(e)
        repo.remove(e)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_education())


class TestPgEducationRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_education(school="Wrong")
        repo.add(original)
        corrected = make_education(school="Corrected")
        repo.replace(original, corrected)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0].school == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        e1 = make_education(
            school="A", start=dt.date(2020, 1, 1), end=dt.date(2021, 1, 1)
        )
        e2 = make_education(
            school="B", start=dt.date(2022, 1, 1), end=dt.date(2023, 1, 1)
        )
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.replace(e1, e2)


class TestPgEducationRepositoryFind:

    def test_find_by_school(self, repo):
        e1 = make_education(school="MIT")
        e2 = make_education(
            school="Stanford", start=dt.date(2018, 9, 1), end=dt.date(2022, 6, 1)
        )
        repo.add(e1)
        repo.add(e2)
        results = repo.find(school="MIT")
        assert len(results) == 1
        assert results[0].school == "MIT"

    def test_find_by_school_case_insensitive(self, repo):
        e = make_education(school="MIT")
        repo.add(e)
        results = repo.find(school="mit")
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        e1 = make_education(school="A")
        e2 = make_education(
            school="B", start=dt.date(2018, 9, 1), end=dt.date(2022, 6, 1)
        )
        repo.add(e1)
        repo.add(e2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")

    def test_find_school_contains(self, repo):
        e1 = make_education(school="Massachusetts Institute of Technology")
        e2 = make_education(
            school="Stanford University",
            start=dt.date(2018, 9, 1),
            end=dt.date(2022, 6, 1),
        )
        repo.add(e1)
        repo.add(e2)
        results = repo.find(school__contains="institute")
        assert len(results) == 1
        assert results[0].school == "Massachusetts Institute of Technology"
