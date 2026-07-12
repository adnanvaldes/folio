import datetime as dt

import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Travel


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    from folio.repositories import PgTravelRepository

    return PgTravelRepository(pg_conn)


def make_travel(**overrides) -> Travel:
    defaults = dict(
        origin="USA",
        destination="CAN",
        date=dt.date(2024, 7, 20),
        note="Business trip",
    )
    return Travel(**{**defaults, **overrides})


class TestPgTravelRepositoryAdd:

    def test_add_and_list(self, repo):
        t = make_travel()
        repo.add(t)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == t

    def test_add_duplicate_raises(self, repo):
        t = make_travel()
        repo.add(t)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(t)

    def test_list_returns_chronological_order(self, repo):
        t1 = make_travel(date=dt.date(2024, 6, 1))
        t2 = make_travel(date=dt.date(2024, 1, 1))
        t3 = make_travel(date=dt.date(2024, 3, 1))
        repo.add(t1)
        repo.add(t2)
        repo.add(t3)
        assert repo.list_all() == [t2, t3, t1]


class TestPgTravelRepositoryDates:

    def test_date_round_trips_as_date_object(self, repo):
        t = make_travel()
        repo.add(t)
        result = repo.list_all()[0]
        assert isinstance(result.date, dt.date)
        assert result.date == dt.date(2024, 7, 20)


class TestPgTravelRepositoryRemove:

    def test_remove_existing(self, repo):
        t = make_travel()
        repo.add(t)
        repo.remove(t)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_travel())


class TestPgTravelRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_travel(note="Wrong")
        repo.add(original)
        corrected = make_travel(note="Corrected")
        repo.replace(original, corrected)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0].note == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        original = make_travel()
        other = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.replace(original, other)


class TestPgTravelRepositoryFind:

    def test_find_by_origin(self, repo):
        t1 = make_travel(origin="USA")
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        repo.add(t1)
        repo.add(t2)
        results = repo.find(origin="USA")
        assert len(results) == 1
        assert results[0].origin == "USA"

    def test_find_no_filters_returns_all(self, repo):
        t1 = make_travel(date=dt.date(2024, 1, 1))
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 6, 1))
        repo.add(t1)
        repo.add(t2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")

    def test_find_by_origin_case_insensitive(self, repo):
        t = make_travel(origin="USA")
        repo.add(t)
        results = repo.find(origin="usa")
        assert len(results) == 1

    def test_find_date_before(self, repo):
        t1 = make_travel(date=dt.date(2020, 1, 1))
        t2 = make_travel(date=dt.date(2024, 6, 1))
        repo.add(t1)
        repo.add(t2)
        results = repo.find(date__before=dt.date(2022, 1, 1))
        assert len(results) == 1
        assert results[0].date == dt.date(2020, 1, 1)

    def test_find_date_after(self, repo):
        t1 = make_travel(date=dt.date(2020, 1, 1))
        t2 = make_travel(date=dt.date(2024, 6, 1))
        repo.add(t1)
        repo.add(t2)
        results = repo.find(date__after=dt.date(2022, 1, 1))
        assert len(results) == 1
        assert results[0].date == dt.date(2024, 6, 1)

    def test_find_note_contains(self, repo):
        t1 = make_travel(note="Business trip")
        t2 = make_travel(destination="MEX", date=dt.date(2024, 1, 1), note="Vacation")
        repo.add(t1)
        repo.add(t2)
        results = repo.find(note__contains="business")
        assert len(results) == 1
        assert results[0].note == "Business trip"
