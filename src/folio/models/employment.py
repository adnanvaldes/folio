from dataclasses import dataclass
from datetime import date, timedelta

from folio.models.record import Record


@dataclass(eq=False)
class Employment(Record["Employment"]):
    """
    Represents a period of employment
    """

    start: date
    end: date | None
    company: str
    supervisor: str
    address: str
    phone: str

    def __str__(self):
        end = self.end or "Present"
        return f"{self.company} ({self.start} -> {end} [{self.duration}])"

    @property
    def duration(self) -> timedelta:
        """
        Returns the duration of employment as a timedelta.
        """
        end_date = self.end or date.today()
        if end_date < self.start:
            raise ValueError("End date cannot be before start date.")
        return end_date - self.start

    def _identity_fields(self):
        """
        Equality and hasing use company name only.
        """
        return (self.company.lower().strip(),)

    def _ordering_fields(self):
        """
        Sort employments by duration (longest first), then start date, then end date.
        """
        end_date = self.end or date.today()
        return (
            -self.duration.days,  # Negative used so that longer durations come first
            self.start,
            self.end,
        )
