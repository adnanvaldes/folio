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

    def __eq__(self, other):
        """
        Two addresses are considered equal if they have the same address, province, country, and postal code. Time periods are not part of an
        address' identity.
        """
        if not isinstance(other, Travel):
            return False
        return (
            self.origin == other.origin
            and self.destination == other.destination
            and self.date == other.date
        )

    def __lt__(self, other):
        if not isinstance(other, Travel):
            return NotImplemented
        return self.date < other.date

    def __hash__(self):
        return hash((self.origin, self.destination, self.date))

    def __str__(self):
        return f"{self.date}: {self.origin} -> {self.destination} ({self.notes})"


@dataclass
class Address(Record["Address"]):
    """
    Represents a primary living address
    """

    ...


@dataclass
class Employment(Record["Employment"]):
    """
    Represents a period of employment
    """

    ...
