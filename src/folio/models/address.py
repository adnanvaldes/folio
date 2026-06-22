import datetime as dt
import dataclasses

@dataclasses.dataclass(frozen=True, eq=False)
class Address:
    """
    Represents a primary living address
    """
    street: str
    city: str
    country: str
    postal_code: str
    start: dt.date
    end: dt.date | None = None
    province: str | None = None

    def __post_init__(self):
        object.__setattr__(self, "street", self.street.strip())
        object.__setattr__(self, "city", self.city.strip())
        object.__setattr__(self, "country", self.country.strip())
        object.__setattr__(self, "postal_code", self.postal_code.strip())
        object.__setattr__(self, "province", self.province.strip() if self.province else None)

        if not isinstance(self.start, dt.date):
            raise TypeError(f"start must be a datetime.date, got {type(self.start)}")

        if not isinstance(self.end, dt.date) and self.end is not None:
            raise TypeError(
                f"end must be a datetime.date or None, got {type(self.end)}"
            )

        if self.end is not None and self.end <= self.start:
            raise ValueError(
                f"end date must be after start date, got: [start={self.start}, end={self.end}]"
            )

        # Strip values to catch empty strings, i.e. ("    ")
        if not self.street:
            raise ValueError("Street is required")
        if not self.city:
            raise ValueError("City is required")
        if not self.country:
            raise ValueError("Country is required")
        if not self.postal_code:
            raise ValueError("Postal code is required")

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

    def __lt__(self, other: "Address") -> bool:
        if not isinstance(other, Address):
            return NotImplemented
        return self.start < other.start

    def __str__(self):
        end = self.end or "Present"
        province = f", {self.province}" if self.province else ""
        return f"{self.street}, {self.city}, {province}, {self.country} {self.postal_code} ({self.start} → {end} [{self.duration}])"

    @property
    def is_open(self) -> bool:
        return self.end is None

    @property
    def duration(self) -> dt.timedelta:
        """
        Returns the duratoin of a stay as a dt.timedelta.
        If end is None, uses today's date.
        """
        return(self.end or dt.date.today()) - self.start

    def overlaps(self, other: "Address") -> bool:
        """
        Returns True if this address's period overlaps with another's.
        end is inclusive: address ending in 2020-12-31 does not overlap
        with one starting 2021-01-01.
        """
        self_end = self.end or dt.date.max
        other_end = other.end or dt.date.max
        return self.start <= other_end and other.start <= self_end

    def close(self, end: dt.date) -> "Address":
        """
        Return a closed version of this Address
        """
        if not self.is_open:
            raise ValueError(f"Address is already closed: {self}")
        if end <= self.start:
            raise ValueError(
                f"Closing date must be after start date, "
                f"got start={self.start}, end={end}"
            )
        return dataclasses.replace(self, end=end)
