import dataclasses
import datetime as dt

from folio.exceptions import FolioStateConflictError, FolioValidationError


@dataclasses.dataclass(eq=False)
class Address:
    """
    Represents a primary living address and period
    """

    street: str
    city: str
    country: str
    postal_code: str
    start: dt.date
    end: dt.date | None = None
    province: str | None = None

    def __post_init__(self):
        self.street = self.street.strip()
        self.city = self.city.strip()
        self.country = self.country.strip()
        self.postal_code = self.postal_code.strip()

        prov = self.province.strip() if self.province else None
        self.province = prov or None

        if not self.street:
            raise FolioValidationError("Street is required")
        if not self.city:
            raise FolioValidationError("City is required")
        if not self.country:
            raise FolioValidationError("Country is required")
        if not self.postal_code:
            raise FolioValidationError("Postal code is required")

        if not isinstance(self.start, dt.date):
            raise TypeError(f"start must be a datetime.date, got {type(self.start)}")

        if not isinstance(self.end, dt.date) and self.end is not None:
            raise TypeError(
                f"end must be a datetime.date or None, got {type(self.end)}"
            )

        if self.end is not None and self.end <= self.start:
            raise FolioValidationError(
                f"end date must be after start date, "
                f"got: [start={self.start}, end={self.end}]"
            )

    def _identity_fields(self) -> tuple:
        """
        Equality and hashing use street address, province, country, and postal code.
        """
        return (
            self.street.lower(),
            self.city.lower(),
            (self.province or "").lower(),
            self.country.lower(),
            self.postal_code.lower(),
            self.start,
            self.end,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return self._identity_fields() == other._identity_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    def _ordering_fields(self) -> tuple:
        return (self.start,)

    def __lt__(self, other: Address) -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    def __str__(self):
        end = self.end or "Present"
        province = f"{self.province}" if self.province else ""
        return (
            f"{self.street}, {self.city}, {province}, "
            f"{self.country} {self.postal_code} "
            f"({self.start} → {end} [{self.duration}])"
        )

    @property
    def is_open(self) -> bool:
        return self.end is None

    @property
    def duration(self) -> dt.timedelta:
        """
        Returns the duration of a stay as a dt.timedelta.
        If end is None, uses today's date.
        """
        return (self.end or dt.date.today()) - self.start

    def overlaps(self, other: Address) -> bool:
        """
        Returns True if this address's period overlaps with another's.
        end is inclusive: address ending in 2020-12-31 does not overlap
        with one starting 2021-01-01.
        """
        self_end = self.end or dt.date.max
        other_end = other.end or dt.date.max
        return self.start <= other_end and other.start <= self_end

    def close(self, end: dt.date) -> Address:
        """
        Return a closed version of this Address
        """
        if not self.is_open:
            raise FolioStateConflictError(f"Address is already closed: {self}")
        if end <= self.start:
            raise FolioValidationError(
                f"Closing date must be after start date, "
                f"got start={self.start}, end={end}"
            )
        return dataclasses.replace(self, end=end)

    def reopen(self) -> Address:
        """
        Return an open version of this address.
        Used in the case where the latest open address is removed and
        the previous one becomes current again.
        """
        if self.is_open:
            raise FolioStateConflictError(f"Address is already open: {self}")
        return dataclasses.replace(self, end=None)
