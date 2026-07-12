import dataclasses
import datetime as dt
import operator as op

from folio.exceptions import (
    FolioDuplicateError,
    FolioNotFoundError,
    FolioValidationError,
)
from folio.models import Address, Book, Education, Employment, FormatType, Travel, Work
from folio.repositories import (
    AddressRepository,
    BookRepository,
    EducationRepository,
    EmploymentRepository,
    TravelRepository,
    WorkRepository,
)
from folio.repositories.sql import parse_filter_key, validate_filter_fields

_CMP = {"before": op.lt, "after": op.gt}


def _match_field(obj, field: str, value, op_name: str | None = None) -> bool:
    """Check if obj.field matches value, with optional operator."""
    actual = getattr(obj, field)
    if op_name == "contains":
        return actual is not None and value.lower() in actual.lower()
    if op_name in _CMP:
        return _CMP[op_name](actual, value)
    if actual is None and value is None:
        return True
    if actual is None or value is None:
        return False
    if isinstance(actual, str):
        return actual.lower().strip() == value.lower().strip()
    return actual == value


class FakeAddressRepository(AddressRepository):

    def __init__(self):
        self._data: set[Address] = set()

    def list_all(self) -> list[Address]:
        return sorted(self._data)

    def add(self, address: Address) -> None:
        if address in self._data:
            raise FolioDuplicateError(f"Address already exists: {address}")
        self._data.add(address)

    def remove(self, address: Address) -> None:
        if address not in self._data:
            raise FolioNotFoundError(f"Address not found: {address}")
        self._data.discard(address)

    def replace(self, old: Address, new: Address) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Address not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Address]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)
            results = {a for a in results if _match_field(a, field, value, op_name)}
        return sorted(results)


class FakeTravelRepository(TravelRepository):

    def __init__(self):
        self._data: set[Travel] = set()

    def list_all(self) -> list[Travel]:
        return sorted(self._data)

    def add(self, travel: Travel) -> None:
        if travel in self._data:
            raise FolioDuplicateError(f"Travel already exists: {travel}")
        self._data.add(travel)

    def remove(self, travel: Travel) -> None:
        if travel not in self._data:
            raise FolioNotFoundError(f"Travel not found: {travel}")
        self._data.discard(travel)

    def replace(self, old: Travel, new: Travel) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Travel not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Travel]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)
            results = {t for t in results if _match_field(t, field, value, op_name)}
        return sorted(results)


class FakeWorkRepository(WorkRepository):

    def __init__(self):
        self._data: set[Work] = set()

    def list_all(self) -> list[Work]:
        return sorted(self._data)

    def add(self, work: Work) -> None:
        if work in self._data:
            raise FolioDuplicateError(f"Work already exists: {work}")
        self._data.add(work)

    def remove(self, work: Work) -> None:
        if work not in self._data:
            raise FolioNotFoundError(f"Work not found: {work}")
        self._data.discard(work)

    def replace(self, old: Work, new: Work) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Work not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Work]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)
            results = {w for w in results if _match_field(w, field, value, op_name)}
        return sorted(results)

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        if work not in self._data:
            raise FolioNotFoundError(f"Work not found: {work}")
        if genre is None and is_read is None:
            raise FolioValidationError("No fields to update")
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

    def list_all(self) -> list[Employment]:
        return sorted(self._data)

    def add(self, employment: Employment) -> None:
        if employment in self._data:
            raise FolioDuplicateError(f"Employment already exists: {employment}")
        self._data.add(employment)

    def remove(self, employment: Employment) -> None:
        if employment not in self._data:
            raise FolioNotFoundError(f"Employment not found: {employment}")
        self._data.discard(employment)

    def replace(self, old: Employment, new: Employment) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Employment not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Employment]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)
            results = {e for e in results if _match_field(e, field, value, op_name)}
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
            raise FolioNotFoundError(f"Employment not found: {employment}")
        if end is None and supervisor is None and address is None and phone is None:
            raise FolioValidationError("No fields to update")
        updated = dataclasses.replace(
            employment,
            end=end if end is not None else employment.end,
            supervisor=supervisor.strip() if supervisor is not None else employment.supervisor,
            address=address.strip() if address is not None else employment.address,
            phone=phone.strip() if phone is not None else employment.phone,
        )
        self._data.discard(employment)
        self._data.add(updated)


class FakeBookRepository(BookRepository):

    def __init__(self):
        self._data: set[Book] = set()

    def list_all(self) -> list[Book]:
        return sorted(self._data)

    def add(self, book: Book) -> None:
        if book in self._data:
            raise FolioDuplicateError(f"Book already exists: {book}")
        self._data.add(book)

    def remove(self, book: Book) -> None:
        if book not in self._data:
            raise FolioNotFoundError(f"Book not found: {book}")
        self._data.discard(book)

    def replace(self, old: Book, new: Book) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Book not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Book]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)

            def _book_match(book: Book) -> bool:
                if field in ("author", "title", "year"):
                    actual = getattr(book.work, field)
                elif field == "format_type":
                    actual = book.format_type.value
                else:
                    actual = getattr(book, field)
                if op_name == "contains":
                    return actual is not None and value.lower() in actual.lower()
                if op_name in _CMP:
                    return _CMP[op_name](actual, value)
                if actual is None and value is None:
                    return True
                if actual is None or value is None:
                    return False
                if field == "format_type":
                    ft = value if isinstance(value, FormatType) else FormatType(value)
                    return book.format_type == ft
                if isinstance(actual, str):
                    return actual.lower().strip() == value.lower().strip()
                return actual == value

            results = {b for b in results if _book_match(b)}
        return sorted(results)


class FakeEducationRepository(EducationRepository):

    def __init__(self):
        self._data: set[Education] = set()

    def list_all(self) -> list[Education]:
        return sorted(self._data)

    def add(self, education: Education) -> None:
        if education in self._data:
            raise FolioDuplicateError(f"Education already exists: {education}")
        self._data.add(education)

    def remove(self, education: Education) -> None:
        if education not in self._data:
            raise FolioNotFoundError(f"Education not found: {education}")
        self._data.discard(education)

    def replace(self, old: Education, new: Education) -> None:
        if old not in self._data:
            raise FolioNotFoundError(f"Education not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> list[Education]:
        validate_filter_fields(filters, self.VALID_FIELDS)
        results = set(self._data)
        for key, value in filters.items():
            field, op_name = parse_filter_key(key)
            results = {e for e in results if _match_field(e, field, value, op_name)}
        return sorted(results)
