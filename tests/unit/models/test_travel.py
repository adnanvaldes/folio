import dataclasses
import datetime as dt

import pytest

from folio.models import Travel


def make_travel(**overrides) -> Travel:
    defaults = dict(
        origin="USA",
        destination="CAN",
        date=dt.date(2024, 7, 20),
        note="Business trip",
    )
    return Travel(**{**defaults, **overrides})


class TestTravelConstruction:

    def test_valid_travel_constructs(self):
        t = make_travel()
        assert t.origin == "USA"
        assert t.destination == "CAN"
        assert t.date == dt.date(2024, 7, 20)
        assert t.note == "Business trip"

    def test_origin_uppercased(self):
        t = make_travel(origin="usa")
        assert t.origin == "USA"

    def test_destination_uppercased(self):
        t = make_travel(destination="can")
        assert t.destination == "CAN"

    def test_origin_stripped(self):
        t = make_travel(origin="  USA  ")
        assert t.origin == "USA"

    def test_destination_stripped(self):
        t = make_travel(destination="  CAN  ")
        assert t.destination == "CAN"

    def test_note_stripped(self):
        t = make_travel(note="  Business trip  ")
        assert t.note == "Business trip"

    def test_rejects_non_date(self):
        with pytest.raises(TypeError, match="date must be a datetime.date"):
            make_travel(date="2024-07-20")

    def test_rejects_empty_origin(self):
        with pytest.raises(ValueError, match="Origin is required"):
            make_travel(origin="")

    def test_rejects_empty_destination(self):
        with pytest.raises(ValueError, match="Destination is required"):
            make_travel(destination="")

    def test_rejects_short_origin(self):
        with pytest.raises(ValueError, match="must be 3 letters"):
            make_travel(origin="US")

    def test_rejects_long_origin(self):
        with pytest.raises(ValueError, match="must be 3 letters"):
            make_travel(origin="USAA")

    def test_rejects_short_destination(self):
        with pytest.raises(ValueError, match="must be 3 letters"):
            make_travel(destination="CA")

    def test_rejects_long_destination(self):
        with pytest.raises(ValueError, match="must be 3 letters"):
            make_travel(destination="CANA")


class TestTravelImmutability:

    def test_cannot_mutate_origin(self):
        t = make_travel()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.origin = "MEX"

    def test_cannot_mutate_date(self):
        t = make_travel()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.date = dt.date(2025, 1, 1)

    def test_cannot_mutate_note(self):
        t = make_travel()
        with pytest.raises(dataclasses.FrozenInstanceError):
            t.note = "Changed"


class TestTravelIdentity:

    def test_equal_travels_are_equal(self):
        t1 = make_travel()
        t2 = make_travel()
        assert t1 == t2

    def test_equal_travels_have_same_hash(self):
        t1 = make_travel()
        t2 = make_travel()
        assert hash(t1) == hash(t2)

    def test_different_origin_not_equal(self):
        t1 = make_travel(origin="USA")
        t2 = make_travel(origin="MEX")
        assert t1 != t2

    def test_different_destination_not_equal(self):
        t1 = make_travel(destination="CAN")
        t2 = make_travel(destination="MEX")
        assert t1 != t2

    def test_different_date_not_equal(self):
        t1 = make_travel(date=dt.date(2024, 7, 20))
        t2 = make_travel(date=dt.date(2024, 7, 21))
        assert t1 != t2

    def test_different_note_still_equal(self):
        t1 = make_travel(note="Trip A")
        t2 = make_travel(note="Trip B")
        assert t1 == t2
        assert hash(t1) == hash(t2)

    def test_not_equal_to_string(self):
        t = make_travel()
        assert t != "USA->CAN"

    def test_not_equal_to_none(self):
        t = make_travel()
        assert t is not None

    def test_usable_as_dict_key(self):
        t = make_travel()
        d = {t: "value"}
        assert d[make_travel()] == "value"

    def test_usable_in_set(self):
        t1 = make_travel()
        t2 = make_travel()
        s = {t1, t2}
        assert len(s) == 1

    def test_case_insensitive_identity(self):
        t1 = make_travel(origin="USA", destination="CAN")
        t2 = make_travel(origin="usa", destination="can")
        assert t1 == t2
        assert hash(t1) == hash(t2)


class TestTravelOrdering:

    def test_earlier_date_is_less_than(self):
        t1 = make_travel(date=dt.date(2024, 1, 1))
        t2 = make_travel(date=dt.date(2024, 6, 1))
        assert t1 < t2

    def test_sorted_orders_by_date(self):
        t1 = make_travel(date=dt.date(2024, 6, 1))
        t2 = make_travel(date=dt.date(2024, 1, 1))
        t3 = make_travel(date=dt.date(2024, 3, 1))
        assert sorted([t1, t2, t3]) == [t2, t3, t1]


class TestTravelStr:

    def test_str_contains_details(self):
        t = make_travel()
        s = str(t)
        assert "USA" in s
        assert "CAN" in s
        assert "2024-07-20" in s
        assert "Business trip" in s
