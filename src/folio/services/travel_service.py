import datetime as dt
from typing import List, Optional
from folio.models import Travel
from folio.uow import UnitOfWork


class TravelService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, origin: str, destination: str, date: dt.date, notes: str = ""):
        date = dt.date.fromisoformat(date)
        travel = Travel(origin=origin, destination=destination, date=date, notes=notes)

        with self.uow:
            uow.travel.add(travel)

    def get(self, travel_id) -> Optional[Travel]:
        with self.uow:
            return self.uow.travel.get(travel_id)

    def list(self) -> List[Travel]:
        with self.uow:
            return self.uow.travel.list()

    def find(self, origin=None, destination=None, date=None) -> List[Travel]:
        with self.uow:
            return self.uow.travel.find(origin, destination, date)
