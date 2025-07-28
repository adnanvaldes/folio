import sqlite3

from ..unit_of_work import UnitOfWork

import folio.repositories as repo


class SQLiteUnitOfWork(UnitOfWork):

    def __init__(self, db_path="folio.db"):
        self.db_path = db_path

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
        self.travel = repo.SQLiteTravelRepository(self.conn)
        return self


class EmploymentSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self.employment = repo.SQLiteEmploymentRepository(self.conn)
        return self


class AddressSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self.address = repo.SQLiteAddressRepository(self.conn)
        return self
