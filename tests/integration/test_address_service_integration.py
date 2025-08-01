import pytest
import sqlite3
import datetime as dt

from folio.models import Address
from folio.services import AddressService
from folio.uow import AddressSQLiteUoW
from folio.repositories import SQLiteAddressRepository


def test_add_and_list_address(fake_db, multiple_addresses):
    uow = AddressSQLiteUoW(fake_db)
    service = AddressService(uow)

    data = multiple_addresses
    new_id = service.add(
        start=data["start"],
        end=data["end"],
        street=data["street"],
        city=data["city"],
        province=data["province"],
        country=data["country"],
        postal_code=data["postal_code"],
    )
    addresses = service.list()

    assert len(addresses) == 1
    addr = addresses[0]
    assert isinstance(addr, Address)
    assert addr.start == data["start"]
    assert addr.end == data["end"]
    assert addr.street == data["street"]
    assert addr.city == data["city"]
    assert addr.province == data["province"]
    assert addr.country == data["country"]
    assert addr.postal_code == data["postal_code"]
    assert new_id == 1


def test_get_address_by_id(fake_db):
    uow = AddressSQLiteUoW(fake_db)
    service = AddressService(uow)

    service.add(
        start="2020-01-01",
        street="123 Some Str",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    address_id = 1
    address = service.get(address_id)

    assert address is not None
    assert address.start == dt.date(2020, 1, 1)
    assert address.country == "Canada"


def test_prevent_duplicate_address(fake_db):
    uow = AddressSQLiteUoW(fake_db)
    service = AddressService(uow)

    service.add(
        start="1900-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )

    with pytest.raises(ValueError) as e:
        service.add(
            start="1900-01-01",
            end="1950-01-01",
            street="123 Some Str",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="V6Y 0A0",
        )

    assert "already exists" in str(e.value)


def test_find_address_by_street(fake_db):
    uow = AddressSQLiteUoW(fake_db)
    service = AddressService(uow)

    service.add(
        start="1901-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    service.add(
        start="1951-01-01",
        end="2000-01-01",
        street="456 Other Street",
        city="Mexico City",
        country="Mexico",
        postal_code="16040",
    )

    results = service.find(street="456 Other Street")
    assert len(results) == 1
    assert results[0].street == "456 Other Street"


def test_delete_by_fields(fake_db):
    uow = AddressSQLiteUoW(fake_db)
    service = AddressService(uow)

    service.add(
        start="1901-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    service.add(
        start="1951-01-01",
        end="2000-01-01",
        street="456 Other Street",
        city="Mexico City",
        country="Mexico",
        postal_code="16040",
    )

    assert len(service.list()) == 2

    service.delete(country="Mexico")
    assert len(service.list()) == 1

    service.delete(postal_code="V6Y 0A0")
    assert service.list() == []

    with pytest.raises(ValueError):
        service.delete(city="Vancouver")
