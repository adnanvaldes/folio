import datetime as dt
from dataclasses import dataclass

from folio.models.record import Record


@dataclass(eq=False)
class Travel(Record["Travel"]):
    """
    Represents a unit of international travel
    """

    origin: str
    destination: str
    date: dt.date
    notes: str

    def __post_init__(self):
        if not isinstance(self.date, dt.date):
            raise TypeError(f"date must be a datetime.date, got {type(self.date)}")

        for country in [self.origin, self.destination]:
            if len(country) != 3 and country.isupper():
                raise TypeError(f"country data must be 3-letters, got {country}")

    def __str__(self):
        return f"{self.date}: {self.origin} -> {self.destination} ({self.notes})"

    def _identity_fields(self):
        """
        Equality and hashing use origin, destination, and date.
        Notes are excluded.
        """
        return (self.origin, self.destination, self.date)

    def _ordering_fields(self):
        """
        Sort by date (earlier first).
        """
        return (self.date,)
