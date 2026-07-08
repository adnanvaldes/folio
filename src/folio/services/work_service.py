from typing import List

from folio.models.work import Work
from folio.uow import UnitOfWork


class WorkService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, work: Work) -> None:
        with self.uow:
            self.uow.work.add(work)

    def remove(self, work: Work) -> None:
        with self.uow:
            self.uow.work.remove(work)

    def replace(self, old: Work, new: Work) -> None:
        with self.uow:
            self.uow.work.replace(old, new)

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        with self.uow:
            self.uow.work.update(work, genre=genre, is_read=is_read)

    def find(self, **filters) -> List[Work]:
        with self.uow:
            return self.uow.work.find(**filters)

    def list(self) -> list[Work]:
        with self.uow:
            return self.uow.work.list()
