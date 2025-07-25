from typing import Optional, List
from abc import ABC, abstractmethod

from folio.models import Travel, Employment, R
from folio.repositories import Repository


class FakeRepository(Repository[R]):
    def __init__(self):
        self._data: dict[int, R] = {}
        self._next_id = 1

    def add(self, R: R) -> int:
        self._data[self._next_id] = R
        self._next_id += 1
        return self._next_id - 1

    def get(self, R_id: int) -> Optional[R]:
        return self._data.get(R_id)

    def list(self) -> List[R]:
        return list(self._data.values())

    @abstractmethod
    def find(self): ...


class FakeTravelRepository(FakeRepository[Travel]):

    def find(
        self, origin: str = None, destination: str = None, date: str = None
    ) -> List[Travel]:
        result = self.list()
        if origin:
            result = [t for t in result if t.origin == origin]
        if destination:
            result = [t for t in result if t.destination == destination]
        if date:
            if isinstance(date, str):
                from datetime import date as Date

                date = Date.fromisoformat(date)
            result = [t for t in result if t.date == date]
        return result
