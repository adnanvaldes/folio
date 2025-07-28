import pytest
import sqlite3
import datetime as dt

from folio.services import EmploymentService
from folio.uow import EmploymentSQLiteUoW
from folio.repositories import SQLiteEmploymentRepository


def test_add_and_list_employment(fake_db, multiple_employments):
    uow = EmploymentSQLiteUoW(fake_db)
    service = EmploymentService(uow)

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
    assert emp.start == data["start"]
    assert emp.end == data["end"]
    assert emp.company == data["company"]
    assert emp.supervisor == data["supervisor"]
    assert emp.address == data["address"]
    assert emp.phone == data["phone"]
    assert new_id == 1


def test_get_employment_by_id(fake_db):
    uow = EmploymentSQLiteUoW(fake_db)
    service = EmploymentService(uow)

    service.add(
        start="2020-01-01",
        end="2022-12-31",
        company="Acme",
        supervisor="Alice",
        address="123 Some St",
        phone="555-1111",
    )

    emp_id = 1
    employment = service.get(emp_id)

    assert employment is not None
    assert employment.start == dt.date(2020, 1, 1)
    assert employment.supervisor == "Alice"


def test_find_employment(fake_db, multiple_employments):
    uow = EmploymentSQLiteUoW(fake_db)
    service = EmploymentService(uow)

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
