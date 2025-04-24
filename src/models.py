from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List
import uuid
import re

from .utils import is_valid_isbn_13, convert_isbn_10_to_13


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
        if isbn is None:
            return None

        if is_valid_isbn_13(isbn):
            return isbn

        isbn_13 = convert_isbn_10_to_13(isbn)
        if isbn_13 is not None:
            return isbn_13

        raise ValueError(f"Invalid ISBN: {isbn} - must be valid ISBN-10 or ISBN-13")


class Review(BaseModel):
    """A book review in the database"""

    book_id: str
    rating: int = Field(2, ge=1, le=3)
    notes: str | None = None
    date_read: int | None = Field(None, ge=1993, le=2100)
