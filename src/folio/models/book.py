from dataclasses import dataclass
from enum import Enum

from folio.models.record import Record
from folio.models.work import Work


@dataclass(eq=False)
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
        Equality and hashing use Work, format, and ISBN
        """
        return (
            self.work,  # uses Work's identity fields
            self.format.value,
            self.isbn or "",
        )

    def _ordering_fields(self):
        """
        Sort by Work, format, ISBN, then pages.
        """
        return (
            *self._identity_fields(),
            (self.pages is None, self.pages),  # None pages sort last
        )
