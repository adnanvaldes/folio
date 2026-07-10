import dataclasses
import datetime as dt

from folio.exceptions import FolioValidationError


@dataclasses.dataclass(frozen=True, eq=False)
class Employment:
    company: str
    start: dt.date
    supervisor: str
    address: str
    phone: str
    end: dt.date | None = None

    def __post_init__(self):
        object.__setattr__(self, "company", self.company.strip())
        object.__setattr__(self, "supervisor", self.supervisor.strip())
        object.__setattr__(self, "address", self.address.strip())
        object.__setattr__(self, "phone", self.phone.strip())

        if not self.company:
            raise FolioValidationError("Company is required")
        if not self.supervisor:
            raise FolioValidationError("Supervisor is required")
        if not self.address:
            raise FolioValidationError("Address is required")
        if not self.phone:
            raise FolioValidationError("Phone is required")

        if not isinstance(self.start, dt.date):
            raise TypeError(f"start must be a datetime.date, got {type(self.start)}")

        if not isinstance(self.end, dt.date) and self.end is not None:
            raise TypeError(
                f"end must be a datetime.date or None, got {type(self.end)}"
            )

        if self.end is not None and self.end < self.start:
            raise FolioValidationError(
                f"end date cannot be before start date, "
                f"got: [start={self.start}, end={self.end}]"
            )

    def _identity_fields(self) -> tuple:
        return (self.company.lower(), self.start)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Employment):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (self.start,)

    def __lt__(self, other: Employment) -> bool:
        if not isinstance(other, Employment):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    @property
    def duration(self) -> dt.timedelta:
        end_date = self.end or dt.date.today()
        if end_date < self.start:
            raise FolioValidationError("End date cannot be before start date.")
        return end_date - self.start

    def __str__(self):
        end = self.end or "Present"
        try:
            dur = self.duration
        except FolioValidationError:
            dur = "N/A"
        return f"{self.company} ({self.start} -> {end} [{dur}])"
