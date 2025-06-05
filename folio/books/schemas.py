from dataclasses import dataclass, asdict
from enum import Enum
from typing import Iterator

WORK_FIELDS = {"title", "author", "year", "genre", "is_read"}
BOOK_FIELDS = {"pages", "format", "isbn"}


class BookFormat(str, Enum):
    print = "print"
    ebook = "ebook"
    audio = "audiobook"

    def __str__(self):
        return self.value


@dataclass
class SearchCriteria:
    title: str = None
    author: str = None
    year: int = None
    year_min: int = None
    year_max: int = None
    genre: str = None
    is_read: bool = None
    pages: int = None
    pages_min: int = None
    pages_max: int = None
    format: BookFormat = None
    isbn: str = None
    work_id: int = None
    book_id: int = None
    limit: int = None

    def is_empty(self) -> bool:
        return all(getattr(self, field) is None for field in vars(self))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UpdateData:
    title: str = None
    author: str = None
    year: int = None
    genre: str = None
    is_read: bool = None
    pages: int = None
    format: BookFormat = None
    isbn: str = None

    def __str__(self) -> str:
        fields_with_data = {
            field: value for field, value in vars(self).items() if value is not None
        }
        if not fields_with_data:
            return "UpdateData()"

        # Find the maximum field name length for alignment
        max_field_length = max(len(field) for field in fields_with_data.keys())

        # Format specifier, :<{max_field_length} means left align text with max_field_length padding
        field_strings = [
            f"{key:<{max_field_length}}: {str(value)}"
            for key, value in fields_with_data.items()
        ]
        return f"\n\t{'\n\t'.join(field_strings)}"

    def __iter__(self):
        for field, value in vars(self).items():
            if value is not None:
                yield field, value

    def to_dict(self) -> dict:
        return asdict(self)

    def is_empty(self) -> bool:
        return all(getattr(self, field) is None for field in vars(self))

    def exclude_none_fields(self) -> "UpdateData":
        filtered_data = {
            field: value for field, value in vars(self).items() if value is not None
        }
        return UpdateData(**filtered_data)

    def split_work_and_book_args(self) -> tuple["UpdateData"]:
        work_updates = {}
        book_updates = {}
        for field, value in vars(self).items():
            if field in WORK_FIELDS:
                work_updates[field] = value
            elif field in BOOK_FIELDS:
                book_updates[field] = value
            else:
                raise ValueError

        return UpdateData(**work_updates), UpdateData(**book_updates)
