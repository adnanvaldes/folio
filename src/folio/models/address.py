import datetime as dt
from dataclasses import dataclass

from folio.models.record import Record


@dataclass(eq=False)
class Address(Record["Address"]):
    """
    Represents a primary living address
    """

    start: dt.date
    end: dt.date | None
    street: str
    city: str
    province: str | None
    country: str
    postal_code: str

    def __post_init__(self):
        if not isinstance(self.start, dt.date):
            raise TypeError(f"start must be a datetime.date, got {type(self.start)}")

        if not isinstance(self.end, dt.date) and self.end is not None:
            raise TypeError(
                f"end must be a datetime.date or None, got {type(self.end)}"
            )

        if self.end is not None and self.end < self.start:
            raise ValueError(
                f"end date cannot be before start date, got: [start={self.start}, end={self.end}]"
            )

    def __str__(self):
        end = self.end or "Present"
        province = f", {self.province}" if self.province else ""
        return f"{self.street}, {self.city}, {province}, {self.country} {self.postal_code} ({self.start} → {end} [{self.duration}])"

    @property
    def duration(self) -> dt.timedelta:
        """
        Returns the duratoin of a stay as a dt.timedelta.
        If end is None, uses today's date.
        """
        end_date = self.end or dt.date.today()
        if end_date < self.start:
            raise ValueError("End date cannot be before start date.")
        return end_date - self.start

    def _identity_fields(self):
        """
        Equality and hashing use street address, province, country, and postal code.
        Time periods are not part of an address' identity.
        """
        return (
            self.street.lower().strip(),
            self.city.lower().strip(),
            (self.province or "").lower().strip(),
            self.country.lower().strip(),
            self.postal_code.lower().strip(),
            self.start,
            self.end,
        )

    def _ordering_fields(self):
        """
        Sort by duration (longest first), then start, then end.
        """
        end_date = self.end or dt.date.today()
        duration = end_date - self.start
        return (
            -duration.days,  # Negative used so that longer durations come first
            self.start,
            self.end,
        )
