from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any

from folio.models.record import Record


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

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"
