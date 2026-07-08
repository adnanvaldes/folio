import datetime as dt
import pytest
from folio.models.address import Address
from folio.services.address_service import AddressService


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


@pytest.fixture
def service(fake_uow):
    return AddressService(fake_uow)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------


class TestAdd:

    def test_add_single_address(self, service):
        addr = make_address()
        service.add(addr)
        assert addr in service.list()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_address())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        addr = make_address()
        service.add(addr)
        with pytest.raises(ValueError, match="already exists"):
            service.add(addr)

    def test_add_automatically_closes_open_address(self, service):
        open_addr = make_address(end=None)
        service.add(open_addr)

        new_addr = make_address(
            street="456 Elm St",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        service.add(new_addr)

        timeline = service.list()
        assert len(timeline) == 2

        original = next(a for a in timeline if a.street == "123 Main St")
        assert not original.is_open
        assert original.end == dt.date(2022, 12, 31)

    def test_add_with_overlap_requires_confirmation(self, service):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        service.add(existing)

        overlapping = make_address(
            street="456 Elm St",
            start=dt.date(2021, 6, 1),
            end=dt.date(2023, 6, 1),
        )
        with pytest.raises(ValueError, match="requires confirmation"):
            service.add(overlapping)

    def test_add_with_correct_replacing_succeeds(self, service):
        existing = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        service.add(existing)

        overlapping = make_address(
            street="456 Elm St",
            start=dt.date(2021, 6, 1),
            end=dt.date(2023, 6, 1),
        )
        service.add(overlapping, replacing=[existing])
        assert overlapping in service.list()


# ---------------------------------------------------------------------------
# remove()
# ---------------------------------------------------------------------------


class TestRemove:

    def test_remove_only_address_leaves_empty_timeline(self, service):
        addr = make_address()
        service.add(addr)
        service.remove(addr)
        assert service.list() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_address())

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

        timeline = service.list()
        assert len(timeline) == 1
        assert timeline[0].is_open
        assert timeline[0].street == "123 Main St"

    def test_remove_middle_address_raises(self, service):
        a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        b = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2021, 12, 31),
        )
        c = make_address(
            street="789 Oak Ave",
            start=dt.date(2022, 1, 1),
            end=None,
        )
        service.add(a)
        service.add(b)
        service.add(c)

        with pytest.raises(ValueError, match="gap"):
            service.remove(b)

    def test_remove_closed_last_address_raises(self, service):
        """
        Removing the last address when it is closed would create a gap
        since the previous one wouldn't become open.
        """
        a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        b = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        service.add(a)
        service.add(b)

        with pytest.raises(ValueError, match="gap"):
            service.remove(b)


# ---------------------------------------------------------------------------
# replace()
# ---------------------------------------------------------------------------


class TestReplace:

    def test_replace_corrects_street_typo(self, service):
        original = make_address(street="123 Main St")
        service.add(original)

        corrected = make_address(street="123 Main Street")
        service.replace(original, corrected)

        timeline = service.list()
        assert len(timeline) == 1
        assert timeline[0].street == "123 Main Street"

    def test_replace_nonexistent_raises(self, service):
        original = make_address()
        other = make_address(street="456 Elm St")

        with pytest.raises(ValueError, match="not found"):
            service.replace(original, other)

    def test_replace_raises_if_new_overlaps_other_records(self, service):
        a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        b = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2022, 12, 31),
        )
        service.add(a)
        service.add(b)

        # Try to extend a so it overlaps b
        extended_a = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2021, 1, 1),
        )
        with pytest.raises(ValueError, match="overlaps"):
            service.replace(a, extended_a)


# ---------------------------------------------------------------------------
# find()
# ---------------------------------------------------------------------------


class TestFind:

    def test_find_by_city(self, service):
        a = make_address(city="Vancouver")
        b = make_address(
            street="456 Elm St",
            city="Toronto",
            start=dt.date(2023, 1, 1),
            end=None,
        )
        service.add(a)
        service.add(b)

        results = service.find(city="Vancouver")
        assert len(results) == 1
        assert results[0].city == "Vancouver"

    def test_find_open_addresses(self, service):
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

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent_field="value")
