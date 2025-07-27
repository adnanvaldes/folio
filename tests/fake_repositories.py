import datetime as dt
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from folio.models import Travel, Employment, R
from folio.repositories import Repository


class FakeRepository(Repository[R]):
    def __init__(self):
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
        self, origin: str = None, destination: str = None, date: dt.date = None
    ) -> List[Travel]:
        filters = {
            "origin": origin.upper() if origin else None,
            "destination": destination.upper() if destination else None,
            "date": date if date else None,
        }

        return self._apply_filters(filters)


class FakeEmploymentRepository(FakeRepository[Employment]):

    def find(
        self,
        start: dt.date = None,
        end: dt.date = None,
        company: str = None,
        supervisor: str = None,
        address: str = None,
        phone: str = None,
    ) -> List[Employment]:
        filters = {
            "start": start if start else None,
            "end": end if end else None,
            "company": company.capitalize() if company else None,
            "supervisor": supervisor.capitalize() if supervisor else None,
            "address": address.capitalize() if address else None,
            "phone": phone,
        }

        return self._apply_filters(filters)
