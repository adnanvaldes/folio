import datetime as dt

import pytest

from folio.models import Address
from folio.services import AddressService
from folio.uow import AddressSQLiteUoW


@pytest.fixture
def service(fake_db):
    return AddressService(AddressSQLiteUoW(fake_db))


def make_address(**overrides) -> Address:
    defaults = dict(
        street="123 Main St",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 12, 31),
    )
    return Address(**{**defaults, **overrides})


class TestAddressServiceIntegration:

    def test_add_and_list(self, service):
        addr = make_address()
        service.add(addr)
        assert addr in service.list_all()

    def test_dates_survive_sqlite_round_trip(self, service):
        """
        Verifies the deprecated implicit date adapter is not being used.
        If it were, this would produce a DeprecationWarning or wrong type.
        """
        addr = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        service.add(addr)
        retrieved = service.list_all()[0]

        assert isinstance(retrieved.start, dt.date)
        assert isinstance(retrieved.end, dt.date)
        assert retrieved.start == dt.date(2020, 1, 1)
        assert retrieved.end == dt.date(2022, 12, 31)

    def test_null_end_survives_round_trip(self, service):
        addr = make_address(end=None)
        service.add(addr)
        retrieved = service.list_all()[0]
        assert retrieved.end is None

    def test_null_province_survives_round_trip(self, service):
        addr = make_address(province=None)
        service.add(addr)
        retrieved = service.list_all()[0]
        assert retrieved.province is None

    def test_automatically_closes_open_address(self, service):
        open_addr = make_address(end=None)
        service.add(open_addr)

        new_addr = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        service.add(new_addr)

        timeline = service.list_all()
        assert len(timeline) == 2

        original = next(a for a in timeline if a.street == "123 Main St")
        assert not original.is_open
        assert original.end == dt.date(2022, 12, 31)

    def test_remove_latest_open_reopens_previous(self, service):
        closed = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        open_addr = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=None,
        )
        service.add(closed)
        service.add(open_addr)
        service.remove(open_addr)

        timeline = service.list_all()
        assert len(timeline) == 1
        assert timeline[0].is_open

    def test_replace_persists_correctly(self, service):
        original = make_address(street="123 Main St")
        service.add(original)

        corrected = make_address(street="123 Main Street")
        service.replace(original, corrected)

        timeline = service.list_all()
        assert len(timeline) == 1
        assert timeline[0].street == "123 Main Street"

    def test_find_open_uses_is_null_in_sql(self, service):
        """
        This test would pass with the fake repo but fail with SQLite
        if find(end=None) generates = NULL instead of IS NULL.
        """
        closed = make_address(end=dt.date(2022, 12, 31))
        open_addr = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        service.add(closed)
        service.add(open_addr)

        results = service.find(end=None)
        assert len(results) == 1
        assert results[0] == open_addr

    def test_transaction_rolls_back_on_failure(self, service):
        """
        If an operation fails mid-transaction, no partial state
        should be committed to the database.
        """
        addr = make_address()
        service.add(addr)

        # Adding a duplicate should fail and roll back
        with pytest.raises(ValueError):
            service.add(addr)

        # Timeline should be unchanged
        assert len(service.list_all()) == 1
