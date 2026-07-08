import os
import tempfile

import pytest

from folio.uow import UnitOfWork
from tests.fake_repositories import (
    FakeAddressRepository,
    FakeTravelRepository,
    FakeWorkRepository,
    FakeEmploymentRepository,
)


class FakeUnitOfWork(UnitOfWork):
    """
    In-memory Unit of Work for unit testing.
    No database, no transactions — just tracks whether commit was called.
    """

    def __init__(self):
        self.addresses = FakeAddressRepository()
        self.travel = FakeTravelRepository()
        self.work = FakeWorkRepository()
        self.employment = FakeEmploymentRepository()
        self.committed = False

    def _start(self):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

    def _cleanup(self):
        pass


@pytest.fixture
def fake_uow():
    """
    A fresh FakeUnitOfWork for each test.
    Each test gets its own isolated in-memory state.
    """
    uow = FakeUnitOfWork()
    uow._start()
    return uow


@pytest.fixture
def fake_db():
    """
    A temporary SQLite database file for integration tests.
    Created fresh for each test, deleted on teardown.
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.remove(path)
