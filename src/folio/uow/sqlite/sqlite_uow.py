from ..unit_of_work import UnitOfWork

from folio.repositories import SqliteTravelRepository


class TravelSQLiteUoW(UnitOfWork):
    def __enter__(self):
        super().__enter__()
        self.travel = SqliteTravelRepository(self.conn)
        return self
