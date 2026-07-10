import datetime as dt

import pytest

from folio.exceptions import FolioDuplicateError
from folio.models import Travel
from folio.services import TravelService
from folio.uow import TravelSQLiteUoW


@pytest.fixture
def service(fake_db):
    uow = TravelSQLiteUoW(fake_db)
    return TravelService(uow)


def make_travel(**overrides) -> Travel:
    defaults = dict(
        origin="USA",
        destination="CAN",
        date=dt.date(2024, 7, 20),
        note="Business trip",
    )
    return Travel(**{**defaults, **overrides})


class TestTravelServiceIntegration:

    def test_add_and_list(self, service):
        t = make_travel()
        service.add(t)
        result = service.list_all()
        assert len(result) == 1
        assert result[0] == t

    def test_dates_survive_sqlite_round_trip(self, service):
        t = make_travel(date=dt.date(2023, 12, 25))
        service.add(t)
        result = service.list_all()[0]
        assert isinstance(result.date, dt.date)
        assert result.date == dt.date(2023, 12, 25)

    def test_remove_and_list(self, service):
        t = make_travel()
        service.add(t)
        service.remove(t)
        assert service.list_all() == []

    def test_replace_persists_correctly(self, service):
        original = make_travel(note="Old note")
        service.add(original)

        corrected = make_travel(note="New note")
        service.replace(original, corrected)

        result = service.list_all()
        assert len(result) == 1
        assert result[0].note == "New note"

    def test_find_by_destination(self, service):
        t1 = make_travel(destination="CAN")
        t2 = make_travel(origin="MEX", destination="USA", date=dt.date(2024, 1, 1))
        service.add(t1)
        service.add(t2)

        results = service.find(destination="CAN")
        assert len(results) == 1

    def test_transaction_rolls_back_on_failure(self, service):
        t = make_travel()
        service.add(t)
        with pytest.raises(FolioDuplicateError):
            service.add(t)  # duplicate — should rollback
        # The first add should still be there
        assert len(service.list_all()) == 1

    def test_add_multiple_orders_by_date(self, service):
        t1 = make_travel(date=dt.date(2024, 6, 1))
        t2 = make_travel(date=dt.date(2024, 1, 1))
        t3 = make_travel(date=dt.date(2024, 3, 1))
        service.add(t1)
        service.add(t2)
        service.add(t3)
        dates = [t.date for t in service.list_all()]
        assert dates == [
            dt.date(2024, 1, 1),
            dt.date(2024, 3, 1),
            dt.date(2024, 6, 1),
        ]
