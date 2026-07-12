from __future__ import annotations

import dataclasses
import datetime as dt

from folio.exceptions import FolioValidationError


@dataclasses.dataclass(eq=False)
class Travel:
    origin: str
    destination: str
    date: dt.date
    note: str

    def __post_init__(self):
        self.origin = self.origin.strip().upper()
        self.destination = self.destination.strip().upper()

        self.note = self.note.strip()

        if not self.origin:
            raise FolioValidationError("Origin is required")
        if not self.destination:
            raise FolioValidationError("Destination is required")

        if len(self.origin) != 3:
            raise FolioValidationError(
                f"Origin country code must be 3 letters, got '{self.origin}'"
            )
        if len(self.destination) != 3:
            raise FolioValidationError(
                f"Destination country code must be 3 letters, got '{self.destination}'"
            )

        if not isinstance(self.date, dt.date):
            raise TypeError(f"date must be a datetime.date, got {type(self.date)}")

    def _identity_fields(self) -> tuple:
        return (self.origin, self.destination, self.date)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Travel):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (self.date,)

    def __lt__(self, other: Travel) -> bool:
        if not isinstance(other, Travel):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    def __str__(self):
        return f"{self.date}: {self.origin} -> {self.destination} ({self.note})"
