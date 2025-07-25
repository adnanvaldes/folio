import datetime as dt
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from folio.models import Travel, Employment, R
from folio.repositories import Repository


class FakeRepository(Repository[R]):
        self._data: Dict[int, R] = {}
        self._next_id = 1

    def add(self, record: R) -> int:
        self._data[self._next_id] = record
        self._next_id += 1
        return self._next_id - 1

    def get(self, record_id: int) -> Optional[R]:
        return self._data.get(record_id)

    def list(self) -> List[R]:
        return list(self._data.values())

    def _apply_filters(self, filters: dict) -> List[R]:
        items = self.list()
        for attr, value in filters.items():
            if value is not None:
                items = [item for item in items if getattr(item, attr) == value]
        return items

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
