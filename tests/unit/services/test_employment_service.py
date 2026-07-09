import datetime as dt
import pytest
from folio.models import Employment
from folio.services import EmploymentService


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


@pytest.fixture
def service(fake_uow):
    return EmploymentService(fake_uow)


class TestAdd:

    def test_add_single_employment(self, service):
        e = make_employment()
        service.add(e)
        assert e in service.list()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_employment())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        e = make_employment()
        service.add(e)
        with pytest.raises(ValueError, match="already exists"):
            service.add(e)

    def test_add_multiple(self, service):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        service.add(e1)
        service.add(e2)
        assert len(service.list()) == 2


class TestRemove:

    def test_remove_existing(self, service):
        e = make_employment()
        service.add(e)
        service.remove(e)
        assert service.list() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_employment())


class TestReplace:

    def test_replace_updates_record(self, service):
        original = make_employment(supervisor="Wrong name")
        service.add(original)

        corrected = make_employment(supervisor="Corrected name")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].supervisor == "Corrected name"

    def test_replace_nonexistent_raises(self, service):
        original = make_employment()
        other = make_employment(company="Other Corp")
        with pytest.raises(ValueError, match="not found"):
            service.replace(original, other)


class TestUpdate:

    def test_update_supervisor(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, supervisor="New Supervisor")
        result = service.list()[0]
        assert result.supervisor == "New Supervisor"

    def test_update_end(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, end=dt.date(2024, 12, 31))
        result = service.list()[0]
        assert result.end == dt.date(2024, 12, 31)

    def test_update_address(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, address="456 Oak Ave")
        result = service.list()[0]
        assert result.address == "456 Oak Ave"

    def test_update_phone(self, service):
        e = make_employment()
        service.add(e)
        service.update(e, phone="555-9999")
        result = service.list()[0]
        assert result.phone == "555-9999"

    def test_update_no_fields_raises(self, service):
        e = make_employment()
        service.add(e)
        with pytest.raises(ValueError, match="No fields to update"):
            service.update(e)

    def test_update_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.update(make_employment(), supervisor="New")


class TestFind:

    def test_find_by_company(self, service):
        e1 = make_employment()
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        service.add(e1)
        service.add(e2)

        results = service.find(company="Acme Corp")
        assert len(results) == 1
        assert results[0].company == "Acme Corp"

    def test_find_by_company_case_insensitive(self, service):
        e = make_employment(company="Acme Corp")
        service.add(e)
        results = service.find(company="acme corp")
        assert len(results) == 1

    def test_find_by_start(self, service):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        service.add(e1)
        service.add(e2)

        results = service.find(start=dt.date(2024, 1, 1))
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, service):
        e1 = make_employment(start=dt.date(2024, 1, 1))
        e2 = make_employment(company="Beta Inc", start=dt.date(2024, 6, 1))
        service.add(e1)
        service.add(e2)
        assert len(service.find()) == 2

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent=True)


class TestList:

    def test_list_orders_by_start(self, service):
        e1 = make_employment(start=dt.date(2024, 6, 1))
        e2 = make_employment(start=dt.date(2024, 1, 1))
        e3 = make_employment(start=dt.date(2024, 3, 1))
        service.add(e1)
        service.add(e2)
        service.add(e3)
        assert service.list() == [e2, e3, e1]
