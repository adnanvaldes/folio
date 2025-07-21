import pytest
import sqlite3
import datetime as dt

from folio.services import TravelService
from folio.uow import TravelSQLiteUoW
from folio.repositories import SQLiteTravelRepository


def test_add_and_list_travel(fake_db):
    uow = TravelSQLiteUoW(fake_db)
    service = TravelService(uow)

    service.add("USA", "FRA", "2025-07-21", notes="Summer trip")
    travels = service.list()

    assert len(travels) == 1

    travel = travels[0]
    assert travel.origin == "USA"
    assert travel.destination == "FRA"
    assert travel.date == dt.date(2025, 7, 21)
    assert travel.notes == "Summer trip"


def test_get_travel_by_id(fake_db):
    uow = TravelSQLiteUoW(fake_db)
    service = TravelService(uow)

    service.add("USA", "FRA", "2025-07-21", notes="Summer trip")
    travel_id = 1
    travel = service.get(travel_id)

    assert travel is not None
    assert travel.origin == "USA"
    assert travel.destination == "FRA"


def test_prevent_duplicate_travel(fake_db):
    uow = TravelSQLiteUoW(fake_db)
    service = TravelService(uow)

    service.add("USA", "FRA", "2025-07-21")

    with pytest.raises(ValueError) as e:
        service.add("USA", "FRA", "2025-07-21")

    assert "already exists" in str(e.value)


def test_find_travel_by_origin(fake_db):
    uow = TravelSQLiteUoW(fake_db)
    service = TravelService(uow)

    service.add("USA", "FRA", "2025-07-21")
    service.add("CAN", "MEX", "2025-08-01")

    results = service.find(origin="USA")
    assert len(results) == 1
    assert results[0].origin == "USA"
