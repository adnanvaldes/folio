import datetime as dt

import pytest

from folio.models import Employment
from folio.services import EmploymentService
from folio.uow import EmploymentSQLiteUoW


@pytest.fixture
def service(fake_db):
    uow = EmploymentSQLiteUoW(fake_db)
    return EmploymentService(uow)


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


class TestEmploymentServiceIntegration:

    def test_add_and_list(self, service):
        e = make_employment()
        service.add(e)
        result = service.list()
        assert len(result) == 1
        assert result[0] == e

    def test_dates_survive_sqlite_round_trip(self, service):
        e = make_employment(start=dt.date(2023, 12, 25))
        service.add(e)
        result = service.list()[0]
        assert isinstance(result.start, dt.date)
        assert result.start == dt.date(2023, 12, 25)

    def test_end_date_round_trips(self, service):
        e = make_employment(end=dt.date(2024, 6, 30))
        service.add(e)
        result = service.list()[0]
        assert isinstance(result.end, dt.date)
        assert result.end == dt.date(2024, 6, 30)

    def test_remove_and_list(self, service):
        e = make_employment()
        service.add(e)
        service.remove(e)
        assert service.list() == []

    def test_replace_persists_correctly(self, service):
        original = make_employment(supervisor="Old name")
        service.add(original)

        corrected = make_employment(supervisor="New name")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].supervisor == "New name"

    def test_update_supervisor(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, supervisor="Updated")
        result = service.list()[0]
        assert result.supervisor == "Updated"

    def test_update_end_date(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, end=dt.date(2024, 12, 31))
        result = service.list()[0]
        assert result.end == dt.date(2024, 12, 31)

    def test_find_by_company(self, service):
        e1 = make_employment()
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        service.add(e1)
        service.add(e2)

        results = service.find(company="Acme Corp")
        assert len(results) == 1

    def test_find_case_insensitive(self, service):
        e = make_employment(company="Acme Corp")
        service.add(e)
        results = service.find(company="acme corp")
        assert len(results) == 1

    def test_transaction_rolls_back_on_failure(self, service):
        e = make_employment()
        service.add(e)
        with pytest.raises(ValueError):
            service.add(e)  # duplicate
        assert len(service.list()) == 1

    def test_add_multiple_orders_by_start(self, service):
        e1 = make_employment(start=dt.date(2024, 6, 1))
        e2 = make_employment(start=dt.date(2024, 1, 1))
        e3 = make_employment(start=dt.date(2024, 3, 1))
        service.add(e1)
        service.add(e2)
        service.add(e3)
        starts = [e.start for e in service.list()]
        assert starts == [
            dt.date(2024, 1, 1),
            dt.date(2024, 3, 1),
            dt.date(2024, 6, 1),
        ]
