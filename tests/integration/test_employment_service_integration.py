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
