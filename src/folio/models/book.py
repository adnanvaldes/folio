from datetime import timedelta
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from folio.models.record import Record
from folio.models.work import Work


class FormatType(Enum):
    PRINT = "print"
    EBOOK = "ebook"
    AUDIO = "audio"


class BookFormat(ABC):

    @property
    @abstractmethod
    def length(self) -> int | None:
        """
        Return a comparable length (pages or minutes)
        """
        ...

    @property
    def format(self) -> str: ...


@dataclass
class TextFormat(BookFormat):
    """
    A textual book, either print or ebook
    """

    pages: int | None
    format_type: FormatType

    def __post_init__(self):
        if self.format_type not in (FormatType.PRINT, FormatType.EBOOK):
            raise ValueError("Invalid format type for text")

    @property
    def length(self) -> int | None:
        return self.pages

    @property
    def format(self):
        return self.format_type.value

    def __str__(self):
        return f"{self.length} ({self.format})"


@dataclass
class AudioFormat(BookFormat):

    duration: timedelta
    narrator: str | None
    format_type: FormatType = FormatType.AUDIO

    @property
    def length(self) -> int:
        return int(self.duration.total_seconds() // 60)

    @property
    def format(self):
        return self.format_type.value

    def __str__(self):
        return f"{self.length} ({self.format}) (Narrator: {self.narrator})"


@dataclass(eq=False)
class Book(Record["Book"]):
    """
    Represents a specific book instance
    """

    work: Work
    format_data: BookFormat
    isbn: str | None

    @property
    def format(self) -> str:
        return self.format_data.format

    @property
    def length(self) -> int | None:
        return self.format_data.length

    def __str__(self):
        return f"{self.work.title} - {self.work.author}: {self.format}, [{self.isbn}]"

    def _identity_fields(self):
        """
        Equality and hashing use Work, format, and ISBN
        """
        return (
            self.work,  # uses Work's identity fields
            self.format,
            self.isbn or "",
        )

    def _ordering_fields(self):
        """
        Sort by Work, format, ISBN, then pages.
        """
        return (
            *self._identity_fields(),
            (self.length is None, self.length),  # None pages sort last
        )
