from folio.models import Travel
from folio.uow import UnitOfWork


class TravelService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, travel: Travel) -> None:
        with self.uow:
            self.uow.travel.add(travel)

    def remove(self, travel: Travel) -> None:
        with self.uow:
            self.uow.travel.remove(travel)

    def replace(self, old: Travel, new: Travel) -> None:
        with self.uow:
            self.uow.travel.replace(old, new)

    def find(self, **filters) -> list[Travel]:
        with self.uow:
            return self.uow.travel.find(**filters)

    def list_all(self) -> list[Travel]:
        with self.uow:
            return self.uow.travel.list_all()
