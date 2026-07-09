import datetime as dt

import pytest

from folio.models import Travel
from folio.services import TravelService


def make_travel(**overrides) -> Travel:
    defaults = dict(
        origin="USA",
        destination="CAN",
        date=dt.date(2024, 7, 20),
        note="Business trip",
    )
    return Travel(**{**defaults, **overrides})


@pytest.fixture
def service(fake_uow):
    return TravelService(fake_uow)


class TestAdd:

    def test_add_single_travel(self, service):
        t = make_travel()
        service.add(t)
        assert t in service.list()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_travel())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        t = make_travel()
        service.add(t)
        with pytest.raises(ValueError, match="already exists"):
            service.add(t)

    def test_add_multiple(self, service):
        t1 = make_travel(date=dt.date(2024, 1, 1))
        t2 = make_travel(
            origin="MEX",
            destination="USA",
            date=dt.date(2024, 6, 1),
        )
        service.add(t1)
        service.add(t2)
        assert len(service.list()) == 2


class TestRemove:

    def test_remove_existing(self, service):
        t = make_travel()
        service.add(t)
        service.remove(t)
        assert service.list() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_travel())


class TestReplace:

    def test_replace_updates_record(self, service):
        original = make_travel(note="Wrong note")
        service.add(original)

        corrected = make_travel(note="Corrected note")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].note == "Corrected note"

    def test_replace_nonexistent_raises(self, service):
        original = make_travel()
        other = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        with pytest.raises(ValueError, match="not found"):
            service.replace(original, other)


class TestFind:

    def test_find_by_origin(self, service):
        t1 = make_travel(origin="USA")
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        service.add(t1)
        service.add(t2)

        results = service.find(origin="USA")
        assert len(results) == 1
        assert results[0].origin == "USA"

    def test_find_by_destination(self, service):
        t1 = make_travel(destination="CAN")
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        service.add(t1)
        service.add(t2)

        results = service.find(destination="CAN")
        assert len(results) == 1

    def test_find_by_date(self, service):
        t1 = make_travel(date=dt.date(2024, 7, 20))
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        service.add(t1)
        service.add(t2)

        results = service.find(date=dt.date(2024, 7, 20))
        assert len(results) == 1

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent=True)
