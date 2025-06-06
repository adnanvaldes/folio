from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from datetime import date
from typing import List

from books.args import BookFormat


class Work(SQLModel, table=True):
    """
    Represents the abstract creative content of a book, independent of its physical form.

    Attributes:
        id: Unique identifier for the work (auto-incremented in DB)
        title: The title of the work
        author: The author of the work
        year: Year the work was first published (can be negative for BCE)
        genre: The literary genre or category of the work
        is_read: Whether the work has been read (automatically set when reviewed)
    """

    __table_args__ = (UniqueConstraint("title", "author", name="unique_title_author"),)

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    year: int | None = None  # Allow for negative years to represent BCE
    genre: str | None = None
    is_read: bool = Field(default=False, index=True)

    books: List["Book"] = Relationship(back_populates="work", cascade_delete=True)
    reviews: List["Review"] = Relationship(back_populates="work", cascade_delete=True)

    def __str__(self):
        if self.is_read:
            read = "Read"
        else:
            read = "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"


class Book(SQLModel, table=True):
    """
    Represents a specific edition or instance of a literary work.

    Attributes:
        id: Unique identifier for the book (auto-incremented in DB)
        pages: Number of pages in this edition
        format: Format of the book (print, audiobook, ebook, etc.)
        isbn: International Standard Book Number (ISBN-13 format)
        work_id: Reference to the literary work this book contains
    """

    id: int | None = Field(default=None, primary_key=True)
    pages: int | None = None
    format: BookFormat | None = Field(default=None, index=True)
    isbn: str | None = Field(None, unique=True)  # ISBN-13 (or ISBN-10 converted to -13)

    work_id: int | None = Field(default=None, foreign_key="work.id", ondelete="CASCADE")
    work: Work | None = Relationship(back_populates="books")

    def __str__(self):
        # Format specifier, :<{number} means left aligned with {number} min field width
        return f"ISBN: {str(self.isbn or 'None'):<13} pages: {str(self.pages or 'None'):<5} format: {str(self.format or 'None'):<10}"

    # def __repr__(self):
    #     return f"REPR ID: {self.id}, pages: {self.pages}, format: {self.format}, isbn: {self.isbn}"

    # TODO
    # This does not currently work, validation needs to be done on the user input side
    # See: https://github.com/fastapi/sqlmodel/issues/52#issuecomment-1311987732
    # @field_validator("isbn", mode="after")
    # def validate_isbn(cls, isbn) -> str | None:
    #     if isbn is None:
    #         return None

    #     if is_valid_isbn_13(isbn):
    #         return isbn

    #     isbn_13 = convert_isbn_10_to_13(isbn)
    #     if isbn_13 is not None:
    #         return isbn_13

    #     raise ValueError(f"Invalid ISBN: {isbn} - must be valid ISBN-10 or ISBN-13")

    # @field_validator("format")
    # def validate_format(cls, format):
    #     return format.lower()


class Review(SQLModel, table=True):
    """
    Represents your review and thoughts about a literary work.

    A review implies that you have read the work, and adding a review
    will automatically mark the associated work as read.

    Attributes:
        id: Unique identifier for the review (auto-incremented in DB)
        work_id: Reference to the literary work being reviewed
        rating: Rating on a 3-point scale (1-3)
        notes: Optional text notes about the work
        date_read: When you finished reading the work
    """

    id: int | None = Field(default=None, primary_key=True)
    work_id: int | None = Field(default=None, foreign_key="work.id", ondelete="CASCADE")
    work: Work | None = Relationship(back_populates="reviews")
    rating: int = Field(default=2, ge=1, le=3)
    notes: str | None = None
    date_read: date = Field(default_factory=date.today)

    # TODO
    # This does not currently work, validation needs to be done on the user input side
    # See: https://github.com/fastapi/sqlmodel/issues/52#issuecomment-1311987732
    # @field_validator("date_read")
    # def validate_date_read(cls, date_read):
    #     # Check if date is in the future
    #     if date_read > date.today():
    #         raise ValueError("Date read cannot be in the future")

    #     return date_read
