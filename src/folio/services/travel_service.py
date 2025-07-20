from datetime import date

from folio.models import Travel
from folio.uow import UnitOfWork


class TravelService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, origin: str, destination: str, date: date, notes: str = ""):
        travel = Travel(origin=origin, destination=destination, date=date, notes=notes)

        with self.uow:
            uow.travel.add(travel)

    def get(self, travel_id):
        with self.uow:
            return uow.travel.get(travel_id)

    def list(self) -> list[Travel]:
        with self.uow:
            return uow.travel.list()
