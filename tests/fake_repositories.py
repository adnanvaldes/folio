import dataclasses
from typing import List

from folio.repositories.base import AddressRepository, TravelRepository, WorkRepository
from folio.models.address import Address
from folio.models.travel import Travel
from folio.models.work import Work


class FakeAddressRepository(AddressRepository):

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
        if old not in self._data:
            raise ValueError(f"Address not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Address]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            results = {a for a in results if getattr(a, field) == value}
        return sorted(results)


class FakeTravelRepository(TravelRepository):

    def __init__(self):
        self._data: set[Travel] = set()

    def list(self) -> list[Travel]:
        return sorted(self._data)

    def add(self, travel: Travel) -> None:
        if travel in self._data:
            raise ValueError(f"Travel already exists: {travel}")
        self._data.add(travel)

    def remove(self, travel: Travel) -> None:
        if travel not in self._data:
            raise ValueError(f"Travel not found: {travel}")
        self._data.discard(travel)

    def replace(self, old: Travel, new: Travel) -> None:
        if old not in self._data:
            raise ValueError(f"Travel not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Travel]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            results = {t for t in results if getattr(t, field) == value}
        return sorted(results)


class FakeWorkRepository(WorkRepository):

    def __init__(self):
        self._data: set[Work] = set()

    def list(self) -> list[Work]:
        return sorted(self._data)

    def add(self, work: Work) -> None:
        if work in self._data:
            raise ValueError(f"Work already exists: {work}")
        self._data.add(work)

    def remove(self, work: Work) -> None:
        if work not in self._data:
            raise ValueError(f"Work not found: {work}")
        self._data.discard(work)

    def replace(self, old: Work, new: Work) -> None:
        if old not in self._data:
            raise ValueError(f"Work not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Work]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            results = {w for w in results if getattr(w, field) == value}
        return sorted(results)

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        if work not in self._data:
            raise ValueError(f"Work not found: {work}")
        if genre is None and is_read is None:
            raise ValueError("No fields to update")
        updated = dataclasses.replace(work, genre=genre or work.genre, is_read=is_read if is_read is not None else work.is_read)
        self._data.discard(work)
        self._data.add(updated)
