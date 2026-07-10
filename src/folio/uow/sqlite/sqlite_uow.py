import sqlite3

import folio.repositories as repo
from folio.interfaces.cli.config import _default_db_path

from ..unit_of_work import UnitOfWork


class SQLiteUnitOfWork(UnitOfWork):

    def __init__(self, db_path=None):
        self.db_path = db_path or _default_db_path()

    def _start(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("BEGIN")
        return self

    def commit(self):
        self.conn.execute("COMMIT")

    def rollback(self):
        self.conn.execute("ROLLBACK")

    def _cleanup(self):
        self.conn.close()


class TravelSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._travel = repo.SQLiteTravelRepository(self.conn)
        return self


class EmploymentSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._employment = repo.SQLiteEmploymentRepository(self.conn)
        return self


class EducationSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._education = repo.SQLiteEducationRepository(self.conn)
        return self


class AddressSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._addresses = repo.SQLiteAddressRepository(self.conn)
        return self


class WorkSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._work = repo.SQLiteWorkRepository(self.conn)
        self._book = repo.SQLiteBookRepository(self.conn)
        return self


class BookSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self._book = repo.SQLiteBookRepository(self.conn)
        self._work = repo.SQLiteWorkRepository(self.conn)
        return self
