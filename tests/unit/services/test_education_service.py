import datetime as dt

import pytest

from folio.models import Education
from folio.services import EducationService


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


@pytest.fixture
def service(fake_uow):
    return EducationService(fake_uow)


class TestAdd:

    def test_add_single_education(self, service):
        e = make_education()
        service.add(e)
        assert e in service.list_all()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_education())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        e = make_education()
        service.add(e)
        with pytest.raises(ValueError, match="already exists"):
            service.add(e)

    def test_add_multiple(self, service):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(
            field="Mathematics",
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        service.add(e1)
        service.add(e2)
        assert len(service.list_all()) == 2


class TestRemove:

    def test_remove_existing(self, service):
        e = make_education()
        service.add(e)
        service.remove(e)
        assert service.list_all() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_education())


class TestReplace:

    def test_replace_updates_record(self, service):
        original = make_education(school="Old School")
        service.add(original)

        corrected = make_education(school="New School")
        service.replace(original, corrected)

        result = service.list_all()
        assert len(result) == 1
        assert result[0].school == "New School"

    def test_replace_nonexistent_raises(self, service):
        original = make_education()
        other = make_education(school="Other School")
        with pytest.raises(ValueError, match="not found"):
            service.replace(original, other)


class TestFind:

    def test_find_by_field(self, service):
        e1 = make_education()
        e2 = make_education(
            field="Mathematics",
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        service.add(e1)
        service.add(e2)

        results = service.find(field="Data Science")
        assert len(results) == 1
        assert results[0].field == "Data Science"

    def test_find_by_field_case_insensitive(self, service):
        e = make_education(field="Data Science")
        service.add(e)
        results = service.find(field="data science")
        assert len(results) == 1

    def test_find_by_school(self, service):
        e1 = make_education()
        e2 = make_education(
            school="UBC",
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        service.add(e1)
        service.add(e2)

        results = service.find(school="Lighthouse Labs")
        assert len(results) == 1

    def test_find_by_start(self, service):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        service.add(e1)
        service.add(e2)

        results = service.find(start=dt.date(2020, 9, 1))
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, service):
        e1 = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        e2 = make_education(
            start=dt.date(2021, 1, 1),
            end=dt.date(2021, 5, 1),
        )
        service.add(e1)
        service.add(e2)
        assert len(service.find()) == 2

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent=True)


class TestList:

    def test_list_orders_by_start(self, service):
        e1 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 6, 1))
        e2 = make_education(start=dt.date(2020, 1, 1), end=dt.date(2020, 6, 1))
        e3 = make_education(start=dt.date(2020, 6, 1), end=dt.date(2020, 12, 1))
        service.add(e1)
        service.add(e2)
        service.add(e3)
        assert service.list_all() == [e2, e3, e1]
