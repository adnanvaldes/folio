from ..unit_of_work import SQLiteUnitOfWork

from folio.repositories import SQLiteTravelRepository


class TravelSQLiteUoW(SQLiteUnitOfWork):
    def _start(self):
        super()._start()
        self.travel = SQLiteTravelRepository(self.conn)
        return self
