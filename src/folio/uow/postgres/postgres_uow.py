import psycopg
import psycopg.rows
from psycopg.rows import DictRow

from folio.repositories import (
    PgAddressRepository,
    PgBookRepository,
    PgEducationRepository,
    PgEmploymentRepository,
    PgTravelRepository,
    PgWorkRepository,
)

from ..unit_of_work import UnitOfWork


class PostgresUnitOfWork(UnitOfWork):

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn: psycopg.Connection[DictRow]

    def _start(self):
        self.conn = psycopg.connect(self.dsn, row_factory=psycopg.rows.dict_row)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def _cleanup(self):
        self.conn.close()


class TravelPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.travel = PgTravelRepository(self.conn)
        return self


class EmploymentPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.employment = PgEmploymentRepository(self.conn)
        return self


class EducationPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.education = PgEducationRepository(self.conn)
        return self


class AddressPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.addresses = PgAddressRepository(self.conn)
        return self


class WorkPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.work = PgWorkRepository(self.conn)
        self.book = PgBookRepository(self.conn)
        return self


class BookPostgresUoW(PostgresUnitOfWork):
    def _start(self):
        super()._start()
        self.book = PgBookRepository(self.conn)
        self.work = PgWorkRepository(self.conn)
        return self
