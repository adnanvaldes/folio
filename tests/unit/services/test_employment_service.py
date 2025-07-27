import datetime as dt
import pytest
from folio.services import EmploymentService
from folio.models import Employment


def test_add_and_list_employment(fake_uow, multiple_employments):
    service = EmploymentService(fake_uow)

    data = multiple_employments
    new_id = service.add(
        start=data["start"],
        end=data["end"],
        company=data["company"],
        supervisor=data["supervisor"],
        address=data["address"],
        phone=data["phone"],
    )
    employments = service.list()

    assert len(employments) == 1
    emp = employments[0]
    assert isinstance(emp, Employment)
    assert emp.start == data["start"]
    assert emp.end == data["end"]
    assert emp.company == data["company"]
    assert emp.supervisor == data["supervisor"]
    assert emp.address == data["address"]
    assert emp.phone == data["phone"]
    assert new_id == 1
    assert fake_uow.committed is True


def test_add_and_list_employment_without_end(fake_uow):
    service = EmploymentService(fake_uow)

    service.add(
        start="2020-01-01",
        company="Pasco",
        supervisor="Dan",
        address="456 Other St",
        phone="666-5678",
    )

    emp = service.list()[0]
    assert emp.end is None

    expected_duration = dt.date.today() - emp.start
    assert emp.duration == expected_duration


def test_prevent_end_before_start(fake_uow):
    service = EmploymentService(fake_uow)

    with pytest.raises(ValueError) as exc_info:
        service.add(
            start="2020-01-01",
            end="1900-01-01",
            company="Pasco",
            supervisor="Dan",
            address="456 Other St",
            phone="666-5678",
        )
        service.add(
            start="2021-02-02",
            end="2021-02-01",
            company="Pasco",
            supervisor="Dan",
            address="456 Other St",
            phone="666-5678",
        )

    assert "end date cannot be before start date" in str(exc_info.value)


def test_prevents_duplicate_employment(fake_uow):
    service = EmploymentService(fake_uow)

    service.add(
        company="Acme",
        supervisor="Wild E. Coyote",
        address="123 Some St",
        phone="555-1234",
        start=dt.date(2020, 1, 1),
        end=dt.date(2025, 7, 21),
    )

    with pytest.raises(ValueError) as exc_info:
        service.add(
            company="Acme",
            supervisor="Some Other",
            address="Different street",
            phone="666-4567",
            start=dt.date(2020, 1, 1),
            end=dt.date(2025, 7, 21),
        )

    assert "already exists" in str(exc_info.value)


def test_find_employment_by_company(fake_uow):
    service = EmploymentService(fake_uow)

    service.add(
        start="2020-01-01",
        end="2022-12-31",
        company="Acme",
        supervisor="Alice",
        address="123 Some St",
        phone="555-1111",
    )
    service.add(
        start="2023-01-01",
        end="2024-06-30",
        company="BetaCorp",
        supervisor="Bob",
        address="456 Other St",
        phone="555-2222",
    )

    results = service.find(company="Acme")
    assert len(results) == 1
    assert results[0].company == "Acme"


def test_find_employment_by_start_date(fake_uow):
    service = EmploymentService(fake_uow)

    service.add(
        start="2020-01-01",
        end="2022-12-31",
        company="Acme",
        supervisor="Alice",
        address="123 Some St",
        phone="555-1111",
    )
    service.add(
        start="2020-01-01",
        end="2024-06-30",
        company="BetaCorp",
        supervisor="Bob",
        address="456 Other St",
        phone="555-2222",
    )
    service.add(
        start="2021-05-01",
        end="2023-04-30",
        company="Gamma LLC",
        supervisor="Carol",
        address="789 Third St",
        phone="555-3333",
    )

    results = service.find(start="2020-01-01")
    assert len(results) == 2
    for emp in results:
        assert emp.start == dt.date(2020, 1, 1)


def test_find_employment_by_supervisor(fake_uow):
    service = EmploymentService(fake_uow)

    service.add(
        start="2019-03-15",
        end="2021-03-14",
        company="Acme",
        supervisor="Alice",
        address="123 Some St",
        phone="555-1111",
    )
    service.add(
        start="2021-04-01",
        end="2023-04-01",
        company="BetaCorp",
        supervisor="Bob",
        address="456 Other St",
        phone="555-2222",
    )
    service.add(
        start="2023-05-01",
        end=None,
        company="Gamma LLC",
        supervisor="Alice",
        address="789 Third St",
        phone="555-3333",
    )

    results = service.find(supervisor="Alice")
    assert len(results) == 2
    for emp in results:
        assert emp.supervisor == "Alice"
