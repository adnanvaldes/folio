import dataclasses


@dataclasses.dataclass(frozen=True, eq=False)
class Work:
    author: str
    title: str
    year: int | None
    genre: str | None
    is_read: bool

    def __post_init__(self):
        if not self.author.strip():
            raise ValueError("Author is required")
        if not self.title.strip():
            raise ValueError("Title is required")
        if self.year is not None and not isinstance(self.year, int):
            raise TypeError(f"year must be an int or None, got {type(self.year)}")

    def _identity_fields(self) -> tuple:
        return (
            self.author.lower().strip(),
            self.title.lower().strip(),
            (self.year is None, self.year),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Work):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (
            self.author.lower().strip(),
            self.title.lower().strip(),
            (self.year is None, self.year),
        )

    def __lt__(self, other: "Work") -> bool:
        if not isinstance(other, Work):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    def __str__(self):
        read = "Read" if self.is_read else "Not read"
        return f"{self.title} by {self.author} (year: {self.year}, {read})"
