import dataclasses
import datetime as dt

import pytest

from folio.models import Education


def make_education(**overrides) -> Education:
    defaults = dict(
        field="Data Science",
        start=dt.date(2020, 9, 1),
        end=dt.date(2020, 12, 1),
        school="Lighthouse Labs",
        city="Vancouver",
        country="Canada",
        credential="Certificate",
    )
    return Education(**{**defaults, **overrides})


class TestEducationConstruction:

    def test_valid_education_constructs(self):
        e = make_education()
        assert e.field == "Data Science"
        assert e.start == dt.date(2020, 9, 1)
        assert e.end == dt.date(2020, 12, 1)
        assert e.school == "Lighthouse Labs"
        assert e.city == "Vancouver"
        assert e.country == "Canada"
        assert e.credential == "Certificate"

    def test_field_stripped(self):
        e = make_education(field="  Data Science  ")
        assert e.field == "Data Science"

    def test_school_stripped(self):
        e = make_education(school="  Lighthouse Labs  ")
        assert e.school == "Lighthouse Labs"

    def test_city_stripped(self):
        e = make_education(city="  Vancouver  ")
        assert e.city == "Vancouver"

    def test_country_stripped(self):
        e = make_education(country="  Canada  ")
        assert e.country == "Canada"

    def test_credential_stripped(self):
        e = make_education(credential="  Certificate  ")
        assert e.credential == "Certificate"

    def test_rejects_empty_field(self):
        with pytest.raises(ValueError, match="Field is required"):
            make_education(field="")

    def test_rejects_empty_school(self):
        with pytest.raises(ValueError, match="School is required"):
            make_education(school="")

    def test_rejects_empty_city(self):
        with pytest.raises(ValueError, match="City is required"):
            make_education(city="")

    def test_rejects_empty_country(self):
        with pytest.raises(ValueError, match="Country is required"):
            make_education(country="")

    def test_rejects_empty_credential(self):
        with pytest.raises(ValueError, match="Credential is required"):
            make_education(credential="")

    def test_rejects_non_date_start(self):
        with pytest.raises(TypeError, match="start must be a datetime.date"):
            make_education(start="2020-09-01")

    def test_rejects_non_date_end(self):
        with pytest.raises(TypeError, match="end must be a datetime.date"):
            make_education(end="2020-12-01")

    def test_rejects_end_before_start(self):
        with pytest.raises(ValueError, match="end date cannot be before start date"):
            make_education(
                start=dt.date(2020, 12, 1),
                end=dt.date(2020, 9, 1),
            )

    def test_accepts_end_equal_to_start(self):
        d = dt.date(2020, 9, 1)
        e = make_education(start=d, end=d)
        assert e.end == d


class TestEducationImmutability:

    def test_cannot_mutate_field(self):
        e = make_education()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.field = "New Field"

    def test_cannot_mutate_start(self):
        e = make_education()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.start = dt.date(2025, 1, 1)

    def test_cannot_mutate_end(self):
        e = make_education()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.end = dt.date(2025, 1, 1)

    def test_cannot_mutate_school(self):
        e = make_education()
        with pytest.raises(dataclasses.FrozenInstanceError):
            e.school = "New School"


class TestEducationIdentity:

    def test_equal_educations_are_equal(self):
        e1 = make_education()
        e2 = make_education()
        assert e1 == e2

    def test_equal_educations_have_same_hash(self):
        e1 = make_education()
        e2 = make_education()
        assert hash(e1) == hash(e2)

    def test_different_field_not_equal(self):
        e1 = make_education(field="Data Science")
        e2 = make_education(field="Mathematics")
        assert e1 != e2

    def test_different_start_not_equal(self):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 5, 1))
        assert e1 != e2

    def test_different_end_not_equal(self):
        e1 = make_education(end=dt.date(2020, 12, 1))
        e2 = make_education(end=dt.date(2021, 6, 1))
        assert e1 != e2

    def test_different_school_not_equal(self):
        e1 = make_education(school="Lighthouse Labs")
        e2 = make_education(school="UBC")
        assert e1 != e2

    def test_different_city_not_equal(self):
        e1 = make_education(city="Vancouver")
        e2 = make_education(city="Toronto")
        assert e1 != e2

    def test_different_country_not_equal(self):
        e1 = make_education(country="Canada")
        e2 = make_education(country="USA")
        assert e1 != e2

    def test_different_credential_not_equal(self):
        e1 = make_education(credential="Certificate")
        e2 = make_education(credential="Diploma")
        assert e1 != e2

    def test_not_equal_to_string(self):
        e = make_education()
        assert e != "Lighthouse Labs"

    def test_not_equal_to_none(self):
        e = make_education()
        assert e is not None

    def test_usable_as_dict_key(self):
        e = make_education()
        d = {e: "value"}
        assert d[make_education()] == "value"

    def test_usable_in_set(self):
        e1 = make_education()
        e2 = make_education()
        s = {e1, e2}
        assert len(s) == 1

    def test_case_insensitive_field_identity(self):
        e1 = make_education(field="Data Science")
        e2 = make_education(field="data science")
        assert e1 == e2
        assert hash(e1) == hash(e2)

    def test_case_insensitive_school_identity(self):
        e1 = make_education(school="Lighthouse Labs")
        e2 = make_education(school="lighthouse labs")
        assert e1 == e2
        assert hash(e1) == hash(e2)


class TestEducationOrdering:

    def test_earlier_start_is_less_than(self):
        e1 = make_education(start=dt.date(2020, 1, 1), end=dt.date(2020, 6, 1))
        e2 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 6, 1))
        assert e1 < e2

    def test_sorted_orders_by_start(self):
        e1 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 6, 1))
        e2 = make_education(start=dt.date(2020, 1, 1), end=dt.date(2020, 6, 1))
        e3 = make_education(start=dt.date(2020, 6, 1), end=dt.date(2020, 12, 1))
        assert sorted([e1, e2, e3]) == [e2, e3, e1]


class TestEducationDuration:

    def test_duration(self):
        e = make_education(
            start=dt.date(2020, 9, 1),
            end=dt.date(2020, 12, 1),
        )
        assert e.duration == dt.timedelta(days=91)


class TestEducationStr:

    def test_str(self):
        e = make_education()
        s = str(e)
        assert "Lighthouse Labs" in s
        assert "Data Science" in s
        assert "2020-09-01" in s
        assert "2020-12-01" in s
        assert "Certificate" in s
