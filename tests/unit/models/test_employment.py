import dataclasses
import datetime as dt

import pytest

from folio.models import Employment


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


class TestEmploymentConstruction:

    def test_valid_employment_constructs(self):
        e = make_employment()
        assert e.company == "Acme Corp"
        assert e.start == dt.date(2024, 1, 1)
        assert e.supervisor == "Jane Doe"
        assert e.address == "123 Main St"
        assert e.phone == "555-0100"
        assert e.end is None

    def test_with_end_date(self):
        e = make_employment(end=dt.date(2024, 12, 31))
        assert e.end == dt.date(2024, 12, 31)

    def test_company_stripped(self):
        e = make_employment(company="  Acme Corp  ")
        assert e.company == "Acme Corp"

    def test_supervisor_stripped(self):
        e = make_employment(supervisor="  Jane Doe  ")
        assert e.supervisor == "Jane Doe"

    def test_address_stripped(self):
        e = make_employment(address="  123 Main St  ")
        assert e.address == "123 Main St"

    def test_phone_stripped(self):
        e = make_employment(phone="  555-0100  ")
        assert e.phone == "555-0100"

    def test_rejects_empty_company(self):
        with pytest.raises(ValueError, match="Company is required"):
            make_employment(company="")

    def test_rejects_empty_supervisor(self):
        with pytest.raises(ValueError, match="Supervisor is required"):
            make_employment(supervisor="")

    def test_rejects_empty_address(self):
        with pytest.raises(ValueError, match="Address is required"):
            make_employment(address="")

    def test_rejects_empty_phone(self):
        with pytest.raises(ValueError, match="Phone is required"):
            make_employment(phone="")

    def test_rejects_non_date_start(self):
        with pytest.raises(TypeError, match="start must be a datetime.date"):
            make_employment(start="2024-01-01")

    def test_rejects_non_date_end(self):
        with pytest.raises(TypeError, match="end must be a datetime.date or None"):
            make_employment(end="2024-12-31")

    def test_rejects_end_before_start(self):
        with pytest.raises(ValueError, match="end date cannot be before start date"):
            make_employment(
                start=dt.date(2024, 6, 1),
                end=dt.date(2024, 1, 1),
            )

    def test_accepts_end_equal_to_start(self):
        d = dt.date(2024, 1, 1)
        e = make_employment(start=d, end=d)
        assert e.end == d


class TestEmploymentImmutability:

    def test_cannot_mutate_company(self):
        e = make_employment()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.company = "New Corp"

    def test_cannot_mutate_start(self):
        e = make_employment()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.start = dt.date(2025, 1, 1)

    def test_cannot_mutate_supervisor(self):
        e = make_employment()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.supervisor = "New Person"

    def test_cannot_mutate_end(self):
        e = make_employment()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.end = dt.date(2024, 6, 1)


class TestEmploymentIdentity:

    def test_equal_employments_are_equal(self):
        e1 = make_employment()
        e2 = make_employment()
        assert e1 == e2

    def test_equal_employments_have_same_hash(self):
        e1 = make_employment()
        e2 = make_employment()
        assert hash(e1) == hash(e2)

    def test_different_company_not_equal(self):
        e1 = make_employment(company="Acme")
        e2 = make_employment(company="Beta")
        assert e1 != e2

    def test_different_start_not_equal(self):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(start=dt.date(2024, 6, 1))
        assert e1 != e2

    def test_different_supervisor_still_equal(self):
        e1 = make_employment(supervisor="Alice")
        e2 = make_employment(supervisor="Bob")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_different_end_still_equal(self):
        e1 = make_employment(end=None)
        e2 = make_employment(end=dt.date(2024, 12, 31))
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_different_address_still_equal(self):
        e1 = make_employment(address="123 Main")
        e2 = make_employment(address="456 Oak")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_different_phone_still_equal(self):
        e1 = make_employment(phone="555-0100")
        e2 = make_employment(phone="555-0200")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_not_equal_to_string(self):
        e = make_employment()
        assert e != "Acme Corp"

    def test_not_equal_to_none(self):
        e = make_employment()
        assert e is not None

    def test_usable_as_dict_key(self):
        e = make_employment()
        d = {e: "value"}
        assert d[make_employment()] == "value"

    def test_usable_in_set(self):
        e1 = make_employment()
        e2 = make_employment()
        s = {e1, e2}
        assert len(s) == 1

    def test_case_insensitive_company_identity(self):
        e1 = make_employment(company="Acme Corp")
        e2 = make_employment(company="acme corp")
        assert e1 == e2
        assert hash(e1) == hash(e2)


class TestEmploymentOrdering:

    def test_earlier_start_is_less_than(self):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(start=dt.date(2024, 6, 1))
        assert e1 < e2

    def test_sorted_orders_by_start(self):
        e1 = make_employment(start=dt.date(2024, 6, 1))
        e2 = make_employment(start=dt.date(2024, 1, 1))
        e3 = make_employment(start=dt.date(2024, 3, 1))
        assert sorted([e1, e2, e3]) == [e2, e3, e1]


class TestEmploymentDuration:

    def test_duration_with_end(self):
        e = make_employment(
            start=dt.date(2024, 1, 1),
            end=dt.date(2024, 12, 31),
        )
        assert e.duration == dt.timedelta(days=365)

    def test_duration_without_end(self):
        e = make_employment(start=dt.date(2024, 1, 1))
        assert e.duration.days >= 0


class TestEmploymentStr:

    def test_str_without_end(self):
        e = make_employment()
        s = str(e)
        assert "Acme Corp" in s
        assert "2024-01-01" in s
        assert "Present" in s

    def test_str_with_end(self):
        e = make_employment(end=dt.date(2024, 12, 31))
        s = str(e)
        assert "Acme Corp" in s
        assert "2024-01-01" in s
        assert "2024-12-31" in s
