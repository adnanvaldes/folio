import dataclasses
from enum import Enum

from folio.models.work import Work


class FormatType(Enum):
    PRINT = "print"
    EBOOK = "ebook"
    AUDIO = "audio"


@dataclasses.dataclass(frozen=True, eq=False)
class Book:
    work: Work
    format_type: FormatType
    isbn: str | None
    pages: int | None = None
    duration_minutes: int | None = None
    narrator: str | None = None

    def __post_init__(self):
        if not isinstance(self.work, Work):
            raise TypeError(f"work must be a Work, got {type(self.work)}")
        if not isinstance(self.format_type, FormatType):
            raise TypeError(
                f"format_type must be a FormatType, got {type(self.format_type)}"
            )

        isbn = self.isbn.strip() if self.isbn else None
        object.__setattr__(self, "isbn", isbn or None)
        narrator = self.narrator.strip() if self.narrator else None
        object.__setattr__(self, "narrator", narrator or None)

        if self.pages is not None and not isinstance(self.pages, int):
            raise TypeError(f"pages must be an int or None, got {type(self.pages)}")
        if self.duration_minutes is not None and not isinstance(
            self.duration_minutes, int
        ):
            raise TypeError(
                f"duration_minutes must be an int or None, got {type(self.duration_minutes)}"
            )

        if self.format_type == FormatType.AUDIO:
            if self.duration_minutes is None:
                raise ValueError("duration_minutes is required for audio books")
        else:
            if self.pages is None:
                raise ValueError("pages is required for text books")

    def _identity_fields(self) -> tuple:
        return (
            *self.work._identity_fields(),
            self.format_type.value,
            (self.isbn or "").lower().strip(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (
            *self.work._ordering_fields(),
            self.format_type.value,
            (self.isbn or "").lower().strip(),
        )

    def __lt__(self, other: "Book") -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    @property
    def length(self) -> int | None:
        if self.format_type == FormatType.AUDIO:
            return self.duration_minutes
        return self.pages

    def __str__(self):
        isbn = self.isbn or "no ISBN"
        return f"{self.work.title} by {self.work.author} ({self.format_type.value}, {isbn})"
