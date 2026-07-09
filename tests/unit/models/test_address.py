import datetime as dt
import pytest
import dataclasses
from folio.models import Address


def make_address(**overrides) -> Address:
    """
    Return a valid Address, optionally overriding specific fields.
    """
    defaults = dict(
        street="123 Main St",
        city="Vancouver",
        country="Canada",
        postal_code="V6Y 0A0",
        start=dt.date(2020, 1, 1),
        end=dt.date(2022, 12, 31),
    )
    return Address(**{**defaults, **overrides})


class TestAddressConstruction:

    def test_valid_address_constructs(self):
        addr = make_address()
        assert addr.street == "123 Main St"
        assert addr.city == "Vancouver"

    def test_strips_whitespace_from_street(self):
        addr = make_address(street="  123 Main St  ")
        assert addr.street == "123 Main St"

    def test_strips_whitespace_from_city(self):
        addr = make_address(city="  Vancouver  ")
        assert addr.city == "Vancouver"

    def test_strips_whitespace_from_country(self):
        addr = make_address(country="  Canada  ")
        assert addr.country == "Canada"

    def test_strips_whitespace_from_postal_code(self):
        addr = make_address(postal_code="  V6Y 0A0  ")
        assert addr.postal_code == "V6Y 0A0"

    def test_strips_whitespace_from_province(self):
        addr = make_address(province="  BC  ")
        assert addr.province == "BC"

    def test_province_none_remains_none(self):
        addr = make_address(province=None)
        assert addr.province is None

    def test_province_empty_string_normalized_to_none(self):
        addr = make_address(province="")
        assert addr.province is None

    def test_province_whitespace_only_normalized_to_none(self):
        addr = make_address(province="   ")
        assert addr.province is None

    def test_rejects_non_date_start(self):
        with pytest.raises(TypeError, match="start must be a datetime.date"):
            make_address(start="2020-01-01")

    def test_rejects_non_date_end(self):
        with pytest.raises(TypeError, match="end must be a datetime.date"):
            make_address(end="2022-01-01")

    def test_rejects_empty_street(self):
        with pytest.raises(ValueError, match="Street is required"):
            make_address(street="")

    def test_rejects_whitespace_only_street(self):
        with pytest.raises(ValueError, match="Street is required"):
            make_address(street="   ")

    def test_rejects_empty_city(self):
        with pytest.raises(ValueError, match="City is required"):
            make_address(city="")

    def test_rejects_empty_country(self):
        with pytest.raises(ValueError, match="Country is required"):
            make_address(country="")

    def test_rejects_empty_postal_code(self):
        with pytest.raises(ValueError, match="Postal code is required"):
            make_address(postal_code="")

    def test_rejects_end_before_start(self):
        with pytest.raises(ValueError, match="end date must be after start date"):
            make_address(
                start=dt.date(2020, 1, 1),
                end=dt.date(2019, 1, 1),
            )

    def test_rejects_end_equal_to_start(self):
        with pytest.raises(ValueError, match="end date must be after start date"):
            make_address(
                start=dt.date(2020, 1, 1),
                end=dt.date(2020, 1, 1),
            )

    def test_open_address_valid(self):
        addr = make_address(end=None)
        assert addr.end is None


class TestAddressImmutability:

    def test_cannot_mutate_street(self):
        addr = make_address()
        with pytest.raises(dataclasses.FrozenInstanceError):
            addr.street = "456 Elm St"

    def test_cannot_mutate_start(self):
        addr = make_address()
        with pytest.raises(dataclasses.FrozenInstanceError):
            addr.start = dt.date(2021, 1, 1)

    def test_cannot_mutate_end(self):
        addr = make_address()
        with pytest.raises(dataclasses.FrozenInstanceError):
            addr.end = dt.date(2023, 1, 1)


class TestAddressIdentity:

    def test_equal_addresses_are_equal(self):
        a1 = make_address()
        a2 = make_address()
        assert a1 == a2

    def test_equal_addresses_have_same_hash(self):
        a1 = make_address()
        a2 = make_address()
        assert hash(a1) == hash(a2)

    def test_case_insensitive_equality(self):
        # "123 MAIN ST" and "123 main st" are the same address
        a1 = make_address(street="123 Main St")
        a2 = make_address(street="123 MAIN ST")
        assert a1 == a2
        assert hash(a1) == hash(a2)

    def test_different_start_not_equal(self):
        a1 = make_address(start=dt.date(2020, 1, 1))
        a2 = make_address(start=dt.date(2021, 1, 1), end=dt.date(2022, 12, 31))
        assert a1 != a2

    def test_different_end_not_equal(self):
        a1 = make_address(end=dt.date(2022, 12, 31))
        a2 = make_address(end=dt.date(2023, 12, 31))
        assert a1 != a2

    def test_different_street_not_equal(self):
        a1 = make_address(street="123 Main St")
        a2 = make_address(street="456 Elm St")
        assert a1 != a2

    def test_not_equal_to_string(self):
        addr = make_address()
        assert addr != "123 Main St"

    def test_not_equal_to_none(self):
        addr = make_address()
        assert addr != None

    def test_usable_as_dict_key(self):
        addr = make_address()
        d = {addr: "value"}
        assert d[make_address()] == "value"

    def test_usable_in_set(self):
        a1 = make_address()
        a2 = make_address()  # equal to a1
        s = {a1, a2}
        assert len(s) == 1


class TestAddressOrdering:

    def test_earlier_start_is_less_than(self):
        a1 = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        a2 = make_address(
            start=dt.date(2020, 1, 1),
        )
        assert a1 < a2

    def test_sorted_orders_by_start_date(self):
        a1 = make_address(
            start=dt.date(2018, 1, 1),
            end=dt.date(2019, 12, 31),
        )
        a2 = make_address(
            street="456 Elm St",
            start=dt.date(2020, 1, 1),
            end=dt.date(2021, 12, 31),
        )
        a3 = make_address(
            street="789 Oak Ave",
            start=dt.date(2022, 1, 1),
        )
        assert sorted([a3, a1, a2]) == [a1, a2, a3]

    def test_ordering_fields_returns_tuple(self):
        addr = make_address()
        assert addr._ordering_fields() == (addr.start,)


class TestAddressProperties:

    def test_is_open_when_no_end(self):
        addr = make_address(end=None)
        assert addr.is_open is True

    def test_is_not_open_when_end_set(self):
        addr = make_address(end=dt.date(2022, 12, 31))
        assert addr.is_open is False

    def test_duration_closed_address(self):
        addr = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2020, 1, 31),
        )
        assert addr.duration == dt.timedelta(days=30)

    def test_duration_open_address_uses_today(self):
        addr = make_address(
            start=dt.date(2020, 1, 1),
            end=None,
        )
        expected = dt.date.today() - dt.date(2020, 1, 1)
        assert addr.duration == expected


class TestAddressBehaviour:

    def test_overlaps_with_overlapping_periods(self):
        a1 = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2021, 12, 31),
        )
        a2 = make_address(
            street="456 Elm St",
            start=dt.date(2021, 6, 1),
            end=dt.date(2022, 12, 31),
        )
        assert a1.overlaps(a2) is True
        assert a2.overlaps(a1) is True

    def test_does_not_overlap_adjacent_periods(self):
        a1 = make_address(
            start=dt.date(2020, 1, 1),
            end=dt.date(2020, 12, 31),
        )
        a2 = make_address(
            street="456 Elm St",
            start=dt.date(2021, 1, 1),
        )
        assert a1.overlaps(a2) is False
        assert a2.overlaps(a1) is False

    def test_two_open_addresses_overlap(self):
        a1 = make_address(start=dt.date(2020, 1, 1), end=None)
        a2 = make_address(
            street="456 Elm St",
            start=dt.date(2021, 1, 1),
            end=None,
        )
        assert a1.overlaps(a2) is True

    def test_close_returns_closed_copy(self):
        addr = make_address(end=None)
        closed = addr.close(end=dt.date(2022, 12, 31))

        assert closed.end == dt.date(2022, 12, 31)
        assert closed.is_open is False

    def test_close_does_not_mutate_original(self):
        addr = make_address(end=None)
        addr.close(end=dt.date(2022, 12, 31))
        assert addr.is_open is True  # unchanged

    def test_close_raises_if_already_closed(self):
        addr = make_address(end=dt.date(2022, 12, 31))
        with pytest.raises(ValueError, match="already closed"):
            addr.close(end=dt.date(2023, 1, 1))

    def test_close_raises_if_end_before_start(self):
        addr = make_address(start=dt.date(2020, 1, 1), end=None)
        with pytest.raises(ValueError):
            addr.close(end=dt.date(2019, 1, 1))

    def test_close_raises_if_end_equal_to_start(self):
        addr = make_address(start=dt.date(2020, 1, 1), end=None)
        with pytest.raises(ValueError):
            addr.close(end=dt.date(2020, 1, 1))

    def test_reopen_returns_open_copy(self):
        addr = make_address(end=dt.date(2022, 12, 31))
        reopened = addr.reopen()

        assert reopened.is_open is True
        assert reopened.end is None

    def test_reopen_does_not_mutate_original(self):
        addr = make_address(end=dt.date(2022, 12, 31))
        addr.reopen()
        assert addr.end == dt.date(2022, 12, 31)  # unchanged

    def test_reopen_raises_if_already_open(self):
        addr = make_address(end=None)
        with pytest.raises(ValueError, match="already open"):
            addr.reopen()
