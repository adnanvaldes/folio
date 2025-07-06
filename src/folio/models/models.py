from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any

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
            and self.author.lower() == other.title.lower()
            and self.year == other.year
        )

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"


@dataclass
class Book(Record["Book"]):
    """
    Represents a specific book instance
    """

    work: Work
    pages: int | None
    format: BookFormat | None
    isbn: str | None

    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.work == other.work and self.isbn == other.isbn
