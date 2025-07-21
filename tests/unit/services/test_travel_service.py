import datetime as dt
import pytest
from folio.services import TravelService
from folio.models import Travel


def test_add_and_list_travel(fake_uow):
    service = TravelService(fake_uow)

    service.add("USA", "FRA", "2025-07-21", notes="Vacation")
    travels = service.list()
    print(travels)

    assert len(travels) == 1
    travel = travels[0]
    assert isinstance(travel, Travel)
    assert travel.origin == "USA"
    assert travel.destination == "FRA"
    assert travel.date == dt.date(2025, 7, 21)
    assert travel.notes == "Vacation"


def test_prevents_duplicate_travel(fake_uow):
    service = TravelService(fake_uow)

    service.add(origin="USA", destination="FRA", date="2025-07-21")

    with pytest.raises(ValueError) as exc_info:
        service.add(origin="USA", destination="FRA", date="2025-07-21")

    assert "already exists" in str(exc_info.value)


def test_find_travel_by_origin(fake_uow):
    service = TravelService(fake_uow)

    service.add(origin="USA", destination="FRA", date="2025-07-21")
    service.add(origin="CAN", destination="FRA", date="2025-08-01")

    results = service.find(origin="USA")
    assert len(results) == 1
    assert results[0].origin == "USA"


def test_find_travel_by_date(fake_uow):
    service = TravelService(fake_uow)

    service.add(origin="USA", destination="FRA", date="2025-07-21")
    service.add(origin="CAN", destination="FRA", date="2025-07-21")
    service.add(origin="MEX", destination="FRA", date="2025-08-01")

    results = service.find(date="2025-07-21")
    assert len(results) == 2
    for travel in results:
        assert travel.date == dt.date(2025, 7, 21)


def test_invalid_country_code_raises(fake_uow):
    service = TravelService(fake_uow)

    with pytest.raises(ValueError):
        service.add(origin="US", destination="FRA", date="2025-07-21")

    with pytest.raises(ValueError):
        service.add(origin="USA", destination="FRANCE", date="2025-07-21")
