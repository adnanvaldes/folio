import datetime as dt
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from folio import models
from folio.repositories import Repository


class FakeRepository(Repository[models.R]):
    def __init__(self):
        self._data: Dict[int, models.R] = {}
        self._next_id = 1

    def add(self, record: models.R) -> int:
        self._data[self._next_id] = record
        self._next_id += 1
        return self._next_id - 1

    def get(self, record_id: int) -> Optional[models.R]:
        return self._data.get(record_id)

    def list(self) -> List[models.R]:
        return list(self._data.values())

    def update(self, key: int, **data) -> int:
        record = self._data.get(key)
        if not record:
            raise ValueError(f"Record with ID {key} not found")

        for field, value in data.items():
            if hasattr(record, field):
                setattr(record, field, value)

        return 1

    def delete(self, key: int | None = None, **filters):
        if key:
            row = self._data.pop(key, 0)
            return row

        matching_keys = []
        for db_key, record in self._data.items():
            matched = True
            for attr, value in filters.items():
                if value is not None and getattr(record, attr, None) != value:
                    matched = False
                    break
            if matched:
                matching_keys.append(db_key)

        for db_key in matching_keys:
            self._data.pop(db_key)

        return len(matching_keys)

    def _apply_filters(self, filters: dict) -> List[models.R]:
        items = self.list()
        for attr, value in filters.items():
            if value is not None:
                items = [item for item in items if getattr(item, attr) == value]
        return items

    @abstractmethod
    def find(self): ...


class FakeTravelRepository(FakeRepository[models.Travel]):

    def find(
        self,
        origin: str | None = None,
        destination: str | None = None,
        date: dt.date | None = None,
    ) -> List[models.Travel]:
        filters = {
            "origin": origin.upper() if origin else None,
            "destination": destination.upper() if destination else None,
            "date": date if date else None,
        }

        return self._apply_filters(filters)


class FakeEmploymentRepository(FakeRepository[models.Employment]):

    def find(
        self,
        start: dt.date | None = None,
        end: dt.date | None = None,
        company: str | None = None,
        supervisor: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> List[models.Employment]:
        filters = {
            "start": start if start else None,
            "end": end if end else None,
            "company": company.capitalize() if company else None,
            "supervisor": supervisor.capitalize() if supervisor else None,
            "address": address.capitalize() if address else None,
            "phone": phone,
        }

        return self._apply_filters(filters)


class FakeAddressRepository(FakeRepository[models.Address]):

    def find(
        self,
        street: str | None = None,
        city: str | None = None,
        country: str | None = None,
        postal_code: str | None = None,
        start: dt.date | None = None,
        end: dt.date | None = None,
        province: str | None = None,
    ):
        filters = {
            "street": street.strip() if street else None,
            "city": city.strip() if city else None,
            "country": country.strip() if country else None,
            "postal_code": postal_code.strip() if postal_code else None,
            "start": dt.date.fromisoformat(start) if isinstance(start, str) else start,
            "end": dt.date.fromisoformat(end) if isinstance(end, str) else end,
            "province": province.strip() if province else None,
        }
        return self._apply_filters(filters)
