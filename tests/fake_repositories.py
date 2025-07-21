from typing import Optional, List
from folio.models import Travel
from folio.repositories import Repository


class FakeTravelRepository(Repository[Travel]):
    def __init__(self):
        self._data: dict[int, Travel] = {}
        self._next_id = 1

    def add(self, travel: Travel) -> int:
        self._data[self._next_id] = travel
        self._next_id += 1
        return self._next_id - 1

    def get(self, travel_id: int) -> Optional[Travel]:
        return self._data.get(travel_id)

    def list(self) -> List[Travel]:
        return list(self._data.values())

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
