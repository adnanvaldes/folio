from datetime import date
from enum import Enum
from typing import Optional, List, Dict, Any
from functools import total_ordering

from folio.models.record import Record


class Work(Record["Work"]):
    """
    Represents a literary work (the concept of a book, rather than a specific instance)
    """

    title: str
    author: str
    year: int | None
    genre: str | None
    is_read: bool

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"

    def _identity_fields(self):
        """
        Defines equality and hashing: same title, author, an dyear
        """
        return (
            self.title.lower().strip(),
            self.author.lower().strip(),
            (self.year is None, self.year),  # None years sort last
        )

    def _ordering_fields(self):
        """
        Defines sorting: same as the identity of a Work
        """
        return self._identity_fields()


class Book(Record["Book"]):
    """
    Represents a specific book instance
    """

    class Format(Enum):
        PRINT = "print"
        AUDIO = "audio"
        EBOOK = "ebook"

    work: Work
    pages: int | None
    format: Format
    isbn: str | None

    def __str__(self):
        return f"{self.work.title} - {self.work.author}: {self.pages}, {self.isbn}, ({self.format})"

    def _identity_fields(self):
        """
        Defines equality and hashing: same Work, format, and ISBN
        """
        return (
            self.work,  # uses Work's identity fields
            self.format.value,
            self.isbn or "",
        )

    def _ordering_fields(self):
        """
        Defines sorting: by identity first, then by page count
        """
        return (
            *self._identity_fields(),
            (self.pages is None, self.pages),  # None pages sort last
        )


class Travel(Record["Travel"]):
    """
    Represents a unit of international travel
    """

    origin: str
    destination: str
    date: date
    notes: str

    def __str__(self):
        return f"{self.date}: {self.origin} -> {self.destination} ({self.notes})"

    def _identity_fields(self):
        """
        Defines equality and hashing: same origin, destination, and date.
        Notes are excluded, since they are not part of the idendity of
        travel itself
        """
        return (self.origin, self.destination, self.date)

    def _ordering_fields(self):
        """
        Defines sorting order: by date.

        Travel is conceptually lesser than other Travel
        if it happened earlier.
        """
        return (self.date,)


class Address(Record["Address"]):
    """
    Represents a primary living address
    """

    start: date
    end: date | None
    street_address: str
    province: str | None
    country: str
    postal_code: str

    def __str__(self):
        end = self.end or "Present"
        province = f", {self.province}" if self.province else ""
        return f"{self.street_address}{province}, {self.country} {self.postal_code} ({self.start} → {end} [{self.duration}])"

    @property
    def duration(self) -> timedelta:
        """
        Returns the duratoin of a stay as a timedelta.
        If end is None, uses today's date.
        """
        end_date = self.end or date.today()
        if end_date < self.start:
            raise ValueError("End date cannot be before start date.")
        return end_date - self.start

    def _identity_fields(self):
        """
        Equality and hashing use street address, province, country, and postal code.
        Time periods are not part of an address' identity.
        """
        return (
            self.street_address.lower().strip(),
            (self.province or "").lower().strip(),
            self.country.lower().strip(),
            self.postal_code.lower().strip(),
        )

    def _ordering_fields(self):
        """
        Sort by duration (longest first), then start, then end.
        """
        end_date = self.end or date.today()
        duration = end_date - self.start
        return (
            -duration.days,  # Negative used so that longer durations come first
            self.start,
            self.end,
        )


class Employment(Record["Employment"]):
    """
    Represents a period of employment
    """

    start: date
    end: date | None
    company: str
    supervisor: str
    address: str
    phone: str

    def __str__(self):
        end = self.end or "Present"
        return f"{self.company} ({self.start} -> {end} [{self.duration}])"

    @property
    def duration(self) -> timedelta:
        """
        Returns the duration of employment as a timedelta.
        """
        end_date = self.end or date.today()
        if end_date < self.start:
            raise ValueError("End date cannot be before start date.")
        return end_date - self.start

    def _identity_fields(self):
        """
        Equality and hasing use company name only.
        """
        return (self.company.lower().strip(),)

    def _ordering_fields(self):
        """
        Sort employments by duration (longest first), then start date, then end date.
        """
        end_date = self.end or date.today()
        return (
            -self.duration.days,  # Negative used so that longer durations come first
            self.start,
            self.end,
        )
