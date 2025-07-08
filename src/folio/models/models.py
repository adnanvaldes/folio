from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, List, Dict, Any
from functools import total_ordering

from folio.models.record import Record


@dataclass
class Work(Record["Work"]):
    """
    Represents a literary work (the concept of a book, rather than a specific instance)
    """

    title: str
    author: str
    year: int | None
    genre: str | None
    is_read: bool

    def __eq__(self, other):
        """
        Two works are equal if they have the same title, author, and year
        """
        if not isinstance(other, Work):
            return False
        return (
            self.title.lower() == other.title.lower()
            and self.author.lower() == other.author.lower()
            and self.year == other.year
        )

    def __hash__(self):
        return hash((self.title.lower(), self.author.lower(), self.year))

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"


@dataclass
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

    def __eq__(self, other):
        """
        Two Book instances are the same if they refer to the same work,
        have the same format, and have the same ISBN. Page numbers are ignored.
        """
        if not isinstance(other, Book):
            return False
        return (
            self.work == other.work
            and self.isbn == other.isbn
            and self.format == other.format
        )

    def __hash__(self):
        return hash((self.work, self.isbn, self.format))

    def __str__(self):
        return f"{self.work.title} - {self.work.author}: {self.pages}, {self.isbn}, ({self.format})"


@total_ordering
@dataclass
class Travel(Record["Travel"]):
    """
    Represents a unit of international travel
    """

    origin: str
    destination: str
    date: date
    notes: str

    def __eq__(self, other):
        """
        Custom equality that does not include notes to compare
        the equality of two trips, since notes are not part
        of the identity of travel itself.
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
