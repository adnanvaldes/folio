import datetime as dt
from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from folio import models
from folio.repositories import Repository

# For new version
from folio.repositories.base import AddressRepository
from folio.models.address import Address, TimelineDiff


class FakeRepository(Repository[models.R]):
    def __init__(self):
        self._data: Dict[int, models.R] = {}
        self._identity_map: Dict[int, int] = {}
        self._next_id = 1

    def add(self, record: models.R) -> int:
        self._data[self._next_id] = record
        self._identity_map[id(record)] = self._next_id
        self._next_id += 1
        return self._next_id - 1

    def get(self, record_id: int) -> Optional[models.R]:
        record = self._data.get(record_id)
        if record:
            self._identity_map[id(record)] = record_id
        return record

    def list(self) -> List[models.R]:
        results = list(self._data.values())
        for key, record in self._data.items():
            self._identity_map[id(record)] = key
        return results

    def update(self, record: models.R, **data) -> int:
        key = self._identity_map.get(id(record))
        if key is None:
            raise ValueError("Record not tracked")
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


class FakeAddressRepository(AddressRepository):

    VALID_FIELDS = {
        "street",
        "city",
        "province",
        "country",
        "postal_code",
        "start",
        "end"
    }

    def __init__(self):
        self._data: set[Address] = set()

    def list(self) -> list[Address]:
        return sorted(self._data)

    def add(self, address: Address) -> None:
        if address in self._data:
            raise ValueError(f"Address already exists: {address}")
        self._data.add(address)

    def remove(self, address: Address) -> None:
        if address not in self._data:
            raise ValueError(f"Address not found: {address}")
        self._data.discard(address)

    def replace(self, old: Address, new: Address) -> None:
       self.remove(old)
       self.add(new)

    def find(self, **filters) -> list[Address]:
        invalid = set(filters) - self.VALID_FILTERS
        if invalid:
            raise ValueError(f"Invalid filters: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            results = {
                address for address in results
                if getattr(address, field) == value
            }
        return sorted(results)


    
class FakeWorkRepository(FakeRepository[models.Work]):

    def find(
        self,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
        is_read: bool | None = False,
    ):
        filters = {
            "author": author.strip() if author else None,
            "title": title.strip() if title else None,
            "year": year if year is not None else None,
            "genre": genre.strip() if genre else None,
            "is_read": is_read if is_read is not None else None,
        }

        return self._apply_filters(filters)
