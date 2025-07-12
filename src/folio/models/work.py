from dataclasses import dataclass

from folio.models.record import Record


@dataclass(eq=False)
class Work(Record["Work"]):
    """
    Represents a literary work (the concept of a book, rather than a specific instance)
    """

    title: str
    author: str
    year: int | None
    genre: str | None
    is_read: bool

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"

    def _identity_fields(self):
        """
        Equality and hasing use title, author, and year.
        """
        return (
            self.author.lower().strip(),
            self.title.lower().strip(),
            (self.year is None, self.year),  # None years sort last
        )

    def _ordering_fields(self):
        """
        Sort by author, then title, then year.
        """
        return self._identity_fields()
