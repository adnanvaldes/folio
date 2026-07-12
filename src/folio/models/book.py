import dataclasses
import re
from enum import Enum

from folio.exceptions import FolioValidationError

from .work import Work


def validate_isbn(isbn: str | None) -> str | None:
    if isbn is None:
        return None
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", isbn)
    if _is_valid_isbn_13(cleaned):
        return cleaned
    converted = _convert_isbn_10_to_13(cleaned)
    if converted is not None:
        return converted
    raise FolioValidationError(f"Invalid ISBN: {isbn}")


def _is_valid_isbn_10(isbn: str) -> bool:
    chars = list(isbn.lower())
    if len(chars) != 10:
        return False
    if chars[9] == "x":
        chars[9] = "10"
    if not all(str(c).isdigit() for c in chars):
        return False
    digits = list(map(int, chars))
    checksum = sum((10 - i) * d for i, d in enumerate(digits))
    return checksum % 11 == 0


def _is_valid_isbn_13(isbn: str) -> bool:
    if len(isbn) != 13 or not all(c.isdigit() for c in isbn):
        return False
    digits = [int(c) for c in isbn]
    checksum = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    return checksum % 10 == 0


def _convert_isbn_10_to_13(isbn: str) -> str | None:
    if not _is_valid_isbn_10(isbn):
        return None
    isbn_13_digits = [9, 7, 8] + [int(c) for c in isbn[:-1]]
    checksum = sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(isbn_13_digits))
    check_digit = 0 if checksum % 10 == 0 else 10 - (checksum % 10)
    return "".join(str(d) for d in isbn_13_digits + [check_digit])


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
        if isbn:
            isbn = validate_isbn(isbn)
        object.__setattr__(self, "isbn", isbn or None)
        narrator = self.narrator.strip() if self.narrator else None
        object.__setattr__(self, "narrator", narrator or None)

        if self.pages is not None and not isinstance(self.pages, int):
            raise TypeError(f"pages must be an int or None, got {type(self.pages)}")
        if self.duration_minutes is not None and not isinstance(
            self.duration_minutes, int
        ):
            raise TypeError(
                f"duration_minutes must be an int or None, "
                f"got {type(self.duration_minutes)}"
            )

        if self.format_type == FormatType.AUDIO:
            if self.duration_minutes is None:
                raise FolioValidationError(
                    "duration_minutes is required for audio books"
                )
        else:
            if self.pages is None:
                raise FolioValidationError("pages is required for text books")

    def _identity_fields(self) -> tuple:
        return (
            *self.work._identity_fields(),
            self.format_type.value,
            (self.isbn or "").lower(),
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
            (self.isbn or "").lower(),
        )

    def __lt__(self, other: Book) -> bool:
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
        return (
            f"{self.work.title} by {self.work.author} "
            f"({self.format_type.value}, {isbn})"
        )
