import dataclasses
from typing import List

import datetime as dt

from folio.repositories import (
    AddressRepository,
    TravelRepository,
    WorkRepository,
    EmploymentRepository,
    BookRepository,
)
from folio.models import Address, Travel, Work, Employment, Book, FormatType


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
        updated = dataclasses.replace(
            work,
            genre=genre or work.genre,
            is_read=is_read if is_read is not None else work.is_read,
        )
        self._data.discard(work)
        self._data.add(updated)


class FakeEmploymentRepository(EmploymentRepository):

    def __init__(self):
        self._data: set[Employment] = set()

    def list(self) -> list[Employment]:
        return sorted(self._data)

    def add(self, employment: Employment) -> None:
        if employment in self._data:
            raise ValueError(f"Employment already exists: {employment}")
        self._data.add(employment)

    def remove(self, employment: Employment) -> None:
        if employment not in self._data:
            raise ValueError(f"Employment not found: {employment}")
        self._data.discard(employment)

    def replace(self, old: Employment, new: Employment) -> None:
        if old not in self._data:
            raise ValueError(f"Employment not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Employment]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            if field == "company" and value is not None:
                results = {
                    e
                    for e in results
                    if e.company.lower().strip() == value.lower().strip()
                }
            else:
                results = {e for e in results if getattr(e, field) == value}
        return sorted(results)

    def update(
        self,
        employment: Employment,
        *,
        end: dt.date | None = None,
        supervisor: str | None = None,
        address: str | None = None,
        phone: str | None = None,
    ) -> None:
        if employment not in self._data:
            raise ValueError(f"Employment not found: {employment}")
        if end is None and supervisor is None and address is None and phone is None:
            raise ValueError("No fields to update")
        kwargs = {}
        if end is not None:
            kwargs["end"] = end
        if supervisor is not None:
            kwargs["supervisor"] = supervisor.strip()
        if address is not None:
            kwargs["address"] = address.strip()
        if phone is not None:
            kwargs["phone"] = phone.strip()
        updated = dataclasses.replace(employment, **kwargs)
        self._data.discard(employment)
        self._data.add(updated)


class FakeBookRepository(BookRepository):

    def __init__(self):
        self._data: set[Book] = set()

    def list(self) -> list[Book]:
        return sorted(self._data)

    def add(self, book: Book) -> None:
        if book in self._data:
            raise ValueError(f"Book already exists: {book}")
        self._data.add(book)

    def remove(self, book: Book) -> None:
        if book not in self._data:
            raise ValueError(f"Book not found: {book}")
        self._data.discard(book)

    def replace(self, old: Book, new: Book) -> None:
        if old not in self._data:
            raise ValueError(f"Book not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Book]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            if field in ("author", "title", "year"):
                if value is None:
                    results = {b for b in results if getattr(b.work, field) is None}
                elif field == "year":
                    results = {b for b in results if b.work.year == value}
                else:
                    results = {
                        b
                        for b in results
                        if getattr(b.work, field).lower().strip()
                        == value.lower().strip()
                    }
            elif field == "format_type":
                ft = value if isinstance(value, FormatType) else FormatType(value)
                results = {b for b in results if b.format_type == ft}
            else:
                if value is None:
                    results = {b for b in results if getattr(b, field) is None}
                else:
                    results = {b for b in results if getattr(b, field) == value}
        return sorted(results)
