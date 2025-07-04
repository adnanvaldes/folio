from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any

from folio.models.record import Record
from folio.models.common import ValidationResult
from folio.services.protocols import Validator, Serializer, Formatter


@dataclass
class Work(Record["Work"]):
    """
    Represents a literary work (the concept of a book, rather than a specific instance)
    """

    id: int | None
    title: str
    author: str
    year: int | None
    genre: str | None
    is_read: bool

    validator: Validator
    serializer: Serializer
    formatter: Formatter

    def validate(self) -> ValidationResult:
        return self.validator.validate(self)

    def to_dict(self) -> Dict[str, Any]:
        return self.serializer.to_dict(self)

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"
