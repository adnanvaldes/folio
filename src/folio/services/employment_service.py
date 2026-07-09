import datetime as dt

from folio.models import Employment
from folio.uow import UnitOfWork


class EmploymentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, employment: Employment) -> None:
        with self.uow:
            self.uow.employment.add(employment)

    def remove(self, employment: Employment) -> None:
        with self.uow:
            self.uow.employment.remove(employment)

    def replace(self, old: Employment, new: Employment) -> None:
        with self.uow:
            self.uow.employment.replace(old, new)

    def update(
        self,
        employment: Employment,
        *,
        end: dt.date | None = None,
        supervisor: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> None:
        with self.uow:
            self.uow.employment.update(
                employment, end=end, supervisor=supervisor, address=address, phone=phone
            )

    def find(self, **filters) -> list[Employment]:
        with self.uow:
            return self.uow.employment.find(**filters)

    def list(self) -> list[Employment]:
        with self.uow:
            return self.uow.employment.list()
