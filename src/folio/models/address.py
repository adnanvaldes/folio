from dataclasses import dataclass
from datetime import date, timedelta

from folio.models.record import Record


@dataclass(eq=False)
class Address(Record["Address"]):
    """
    Represents a primary living address
    """

    start: date
    end: date | None
    street_address: str
    province: str | None
    country: str
    postal_code: str

    def __str__(self):
        end = self.end or "Present"
        province = f", {self.province}" if self.province else ""
        return f"{self.street_address}{province}, {self.country} {self.postal_code} ({self.start} → {end} [{self.duration}])"

    @property
    def duration(self) -> timedelta:
        """
        Returns the duratoin of a stay as a timedelta.
        If end is None, uses today's date.
        """
        end_date = self.end or date.today()
        if end_date < self.start:
            raise ValueError("End date cannot be before start date.")
        return end_date - self.start

    def _identity_fields(self):
        """
        Equality and hashing use street address, province, country, and postal code.
        Time periods are not part of an address' identity.
        """
        return (
            self.street_address.lower().strip(),
            (self.province or "").lower().strip(),
            self.country.lower().strip(),
            self.postal_code.lower().strip(),
        )

    def _ordering_fields(self):
        """
        Sort by duration (longest first), then start, then end.
        """
        end_date = self.end or date.today()
        duration = end_date - self.start
        return (
            -duration.days,  # Negative used so that longer durations come first
            self.start,
            self.end,
        )
