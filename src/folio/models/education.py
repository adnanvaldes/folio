import dataclasses
import datetime as dt

from folio.exceptions import FolioValidationError


@dataclasses.dataclass(eq=False)
class Education:
    field: str
    start: dt.date
    end: dt.date
    school: str
    city: str
    country: str
    credential: str

    def __post_init__(self):
        self.field = self.field.strip()
        self.school = self.school.strip()
        self.city = self.city.strip()
        self.country = self.country.strip()
        self.credential = self.credential.strip()

        if not self.field:
            raise FolioValidationError("Field is required")
        if not self.school:
            raise FolioValidationError("School is required")
        if not self.city:
            raise FolioValidationError("City is required")
        if not self.country:
            raise FolioValidationError("Country is required")
        if not self.credential:
            raise FolioValidationError("Credential is required")

        if not isinstance(self.start, dt.date):
            raise TypeError(f"start must be a datetime.date, got {type(self.start)}")

        if not isinstance(self.end, dt.date):
            raise TypeError(f"end must be a datetime.date, got {type(self.end)}")

        if self.end < self.start:
            raise FolioValidationError(
                f"end date cannot be before start date, "
                f"got: [start={self.start}, end={self.end}]"
            )

    def _identity_fields(self) -> tuple:
        return (
            self.field.lower(),
            self.start,
            self.end,
            self.school.lower(),
            self.city.lower(),
            self.country.lower(),
            self.credential.lower(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Education):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (self.start,)

    def __lt__(self, other: Education) -> bool:
        if not isinstance(other, Education):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    @property
    def duration(self) -> dt.timedelta:
        return self.end - self.start

    def __str__(self):
        return (
            f"{self.school} — {self.field} ({self.start} → {self.end} "
            f"[{self.duration}], {self.credential})"
        )
