import datetime as dt
import sqlite3

import pytest

from folio.models import Education
from folio.repositories import SQLiteEducationRepository


@pytest.fixture
def repo(fake_db):
    conn = sqlite3.connect(fake_db)
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN")
    repo = SQLiteEducationRepository(conn)
    yield repo
    conn.close()


def make_education(**overrides) -> Education:
    defaults = dict(
        field="Data Science",
        start=dt.date(2020, 9, 1),
        end=dt.date(2020, 12, 1),
        school="Lighthouse Labs",
        city="Vancouver",
        country="Canada",
        credential="Certificate",
    )
    return Education(**{**defaults, **overrides})


class TestSQLiteEducationRepositoryAdd:

    def test_add_and_list(self, repo):
        e = make_education()
        repo.add(e)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == e

    def test_add_duplicate_raises(self, repo):
        e = make_education()
        repo.add(e)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(e)

    def test_add_duplicate_case_insensitive_raises(self, repo):
        e1 = make_education(field="Data Science")
        e2 = make_education(field="data science")
        repo.add(e1)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(e2)

    def test_list_returns_chronological_order(self, repo):
        e1 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 6, 1))
        e2 = make_education(start=dt.date(2020, 1, 1), end=dt.date(2020, 6, 1))
        e3 = make_education(start=dt.date(2020, 6, 1), end=dt.date(2020, 12, 1))
        repo.add(e1)
        repo.add(e2)
        repo.add(e3)
        assert repo.list_all() == [e2, e3, e1]

    def test_same_field_different_dates_allowed(self, repo):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 5, 1))
        repo.add(e1)
        repo.add(e2)
        assert len(repo.list_all()) == 2


class TestSQLiteEducationRepositoryDates:

    def test_date_round_trips_as_date_object(self, repo):
        e = make_education()
        repo.add(e)
        result = repo.list_all()[0]
        assert isinstance(result.start, dt.date)
        assert result.start == dt.date(2020, 9, 1)

    def test_end_date_round_trips(self, repo):
        e = make_education()
        repo.add(e)
        result = repo.list_all()[0]
        assert isinstance(result.end, dt.date)
        assert result.end == dt.date(2020, 12, 1)


class TestSQLiteEducationRepositoryRemove:

    def test_remove_existing(self, repo):
        e = make_education()
        repo.add(e)
        repo.remove(e)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(ValueError, match="not found"):
            repo.remove(make_education())


class TestSQLiteEducationRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_education(school="Old School")
        repo.add(original)

        corrected = make_education(school="New School")
        repo.replace(original, corrected)

        result = repo.list_all()
        assert len(result) == 1
        assert result[0].school == "New School"

    def test_replace_nonexistent_raises(self, repo):
        original = make_education()
        other = make_education(school="Other School")
        with pytest.raises(ValueError, match="not found"):
            repo.replace(original, other)


class TestSQLiteEducationRepositoryFind:

    def test_find_by_field(self, repo):
        e1 = make_education()
        e2 = make_education(
            field="Mathematics",
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        repo.add(e1)
        repo.add(e2)

        results = repo.find(field="Data Science")
        assert len(results) == 1
        assert results[0].field == "Data Science"

    def test_find_by_field_case_insensitive(self, repo):
        e = make_education(field="Data Science")
        repo.add(e)
        results = repo.find(field="data science")
        assert len(results) == 1

    def test_find_by_school(self, repo):
        e1 = make_education()
        e2 = make_education(
            school="UBC",
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        repo.add(e1)
        repo.add(e2)

        results = repo.find(school="Lighthouse Labs")
        assert len(results) == 1

    def test_find_by_start(self, repo):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        repo.add(e1)
        repo.add(e2)

        results = repo.find(start=dt.date(2020, 9, 1))
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        repo.add(e1)
        repo.add(e2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            repo.find(invalid="x")
