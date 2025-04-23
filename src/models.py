from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List
import uuid
import re


class Author(BaseModel):
    """Represents contributor to a book; can be author or editor, translator, etc. as required"""

    name: str
    role: str = "author"  # To allow for translators, or books with multiple authors


class Book(BaseModel):
    """Represents a book in the database"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    contributors: List[Author]
    year_published: int | None = None  # Allow for negative years to represent BCE
    genre: str | None = None
    pages: int | None = None
    isbn: str | None = None  # ISBN-13 (or ISBN-10 converted to -13)

    # Translation information
    year_translated: int | None = None
    original_language: str | None = None

    @validator("isbn")
    def validate_isbn(cls, isbn):
        pass
        # if isbn is None:
        #     return None

        # isbn = re.sub(r"[^a-zA-Z0-9]", "", isbn)

        # # Check ISBN-10
        # if is_isbn_10(isbn):
        #     if isbn[-1]:
        #         pass
        # # TODO


class Review(BaseModel):
    """A book review in the database"""

    book_id: str
    rating: int = Field(2, ge=1, le=3)
    notes: str | None = None
    date_read: int | None = Field(None, ge=1993, le=2100)
