import datetime as dt

import pytest

from folio.models import Education
from folio.services import EducationService
from folio.uow import EducationSQLiteUoW


@pytest.fixture
def service(fake_db):
    uow = EducationSQLiteUoW(fake_db)
    return EducationService(uow)


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


class TestEducationServiceIntegration:

    def test_add_and_list(self, service):
        e = make_education()
        service.add(e)
        result = service.list_all()
        assert len(result) == 1
        assert result[0] == e

    def test_dates_survive_sqlite_round_trip(self, service):
        e = make_education(start=dt.date(2020, 9, 1), end=dt.date(2020, 12, 1))
        service.add(e)
        result = service.list_all()[0]
        assert isinstance(result.start, dt.date)
        assert result.start == dt.date(2020, 9, 1)
        assert isinstance(result.end, dt.date)
        assert result.end == dt.date(2020, 12, 1)

    def test_remove_and_list(self, service):
        e = make_education()
        service.add(e)
        service.remove(e)
        assert service.list_all() == []

    def test_replace_persists_correctly(self, service):
        original = make_education(school="Old School")
        service.add(original)

        corrected = make_education(school="New School")
        service.replace(original, corrected)

        result = service.list_all()
        assert len(result) == 1
        assert result[0].school == "New School"

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

    def test_find_case_insensitive(self, service):
        e = make_education(field="Data Science")
        service.add(e)
        results = service.find(field="data science")
        assert len(results) == 1

    def test_transaction_rolls_back_on_failure(self, service):
        e = make_education()
        service.add(e)
        with pytest.raises(ValueError):
            service.add(e)  # duplicate
        assert len(service.list_all()) == 1

    def test_add_multiple_orders_by_start(self, service):
        e1 = make_education(start=dt.date(2021, 1, 1), end=dt.date(2021, 6, 1))
        e2 = make_education(start=dt.date(2020, 1, 1), end=dt.date(2020, 6, 1))
        e3 = make_education(start=dt.date(2020, 6, 1), end=dt.date(2020, 12, 1))
        service.add(e1)
        service.add(e2)
        service.add(e3)
        starts = [e.start for e in service.list_all()]
        assert starts == [
            dt.date(2020, 1, 1),
            dt.date(2020, 6, 1),
            dt.date(2021, 1, 1),
        ]
