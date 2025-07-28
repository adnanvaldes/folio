import datetime as dt
import pytest
from folio.services import AddressService
from folio.models import Address


def test_add_and_list_address(fake_uow, multiple_addresses):
    service = AddressService(fake_uow)

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
    assert fake_uow.committed is True


def test_add_and_list_address_without_end_or_province(fake_uow):
    service = AddressService(fake_uow)

    service.add(
        start="2020-01-01",
        street="123 Some Str",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
    )

    addr = service.list()[0]
    assert addr.end is None
    assert addr.province is None

    expected_duration = dt.date.today() - addr.start
    assert addr.duration == expected_duration


def test_prevent_end_before_start(fake_uow):
    service = AddressService(fake_uow)

    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="2020-01-01",
            end="1900-01-01",
            street="123 Some Str",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="V6Y 0A0",
        )

    assert "end date cannot be before start date" in str(exc_info.value)


def test_prevents_duplicate_address(fake_uow):
    service = AddressService(fake_uow)

    service.add(
        start="1900-01-01",
        end="1950-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )

    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="1900-01-01",
            end="1950-01-01",
            street="123 Some Str",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="V6Y 0A0",
        )

    assert "already exists" in str(exc_info.value)


def test_find_address_by_street(fake_uow):
    service = AddressService(fake_uow)

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


def test_find_address_by_start_date(fake_uow):
    service = AddressService(fake_uow)

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
        start="2000-01-01",
        end="2020-01-01",
        street="789 Avenue",
        city="Delhi",
        country="India",
        postal_code="Postal 123",
    )

    results = service.find(start="1901-01-01")
    assert len(results) == 1
    for addr in results:
        assert addr.start == dt.date(1901, 1, 1)


def test_find_address_by_country(fake_uow):
    service = AddressService(fake_uow)

    service.add(
        start="1901-01-01",
        end="1950-01-01",
        street="456 Other Street",
        city="Mexico City",
        country="Mexico",
        postal_code="16040",
    )
    service.add(
        start="1951-01-01",
        end="2000-01-01",
        street="123 Some Str",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="V6Y 0A0",
    )
    service.add(
        start="2001-01-01",
        end="2020-01-01",
        street="789 Avenue",
        city="Delhi",
        country="India",
        postal_code="Postal 123",
    )

    results = service.find(country="Mexico")
    assert len(results) == 1
    for addr in results:
        assert addr.country == "Mexico"


def test_prevents_overlaps_addresses(fake_uow):
    service = AddressService(fake_uow)

    service.add(
        start="2020-01-01",
        end="2022-01-01",
        street="123 Main St",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="A1B2C3",
    )

    # Overlapping start date inside existing range
    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="2021-12-01",
            end="2023-01-01",
            street="123 Main St",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="A1B2C3",
        )
    assert "overlaps" in str(exc_info.value).lower()

    # Overlapping end date inside existing range
    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="2019-01-01",
            end="2020-06-01",
            street="123 Main St",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="A1B2C3",
        )
    assert "overlaps" in str(exc_info.value).lower()

    # Address fully inside existing range
    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="2020-06-01",
            end="2021-06-01",
            street="123 Main St",
            city="Vancouver",
            province="BC",
            country="Canada",
            postal_code="A1B2C3",
        )
    assert "overlaps" in str(exc_info.value).lower()

    # Address with no overlap - shoulc succeed
    service.add(
        start="2022-02-01",
        end="2023-01-01",
        street="123 Main St",
        city="Vancouver",
        province="BC",
        country="Canada",
        postal_code="A1B2C3",
    )

    assert fake_uow.committed is True
