from typing import Optional, List
from abc import ABC, abstractmethod

from folio.models import Record, R
from folio.models.address import Address
from folio.models.timeline import TimelineDiff
from folio.models.travel import Travel


class Repository[R: Record](ABC):
    @abstractmethod
    def add(self, record: R) -> int:
        """
        Add a new record to the repository and return its assigned ID
        """
        ...

    @abstractmethod
    def get(self, id: int) -> Optional[R]:
        """
        Retrieve a record by its repository-assigned ID
        """
        ...

    @abstractmethod
    def list(self) -> List[R]:
        """
        Retrun all records in the repository
        """
        ...


class AddressRepository(ABC):

    VALID_FIELDS = {
        "street",
        "city",
        "province",
        "country",
        "postal_code",
        "start",
        "end",
    }

    @abstractmethod
    def list(self) -> List[Address]:
        """
        Return full residence timeline in chronological order
        """
        ...

    @abstractmethod
    def add(self, address: Address) -> None:
        """
        Add a new address to the timeline.
        Raises ValueError if the address exists already.
        """
        ...

    @abstractmethod
    def remove(self, address: Address) -> None:
        """
        Remove an address from the timeline.
        Raises ValueError if the address does not exist.
        """
        ...

    @abstractmethod
    def replace(self, old: Address, new: Address) -> None:
        """
        Replaces old with new. Raises ValueError if old does not exist.
        The caller is responsible for ensuring consitency with the rest
        of the timeline.
        """
        ...

    @abstractmethod
    def find(self, **filters) -> List[Address]:
        """
        Return all addresses matching the given filters.
        Omitting a field means do not filter on that field.
        Passing None for a field means matching on NULL.
        Raises ValueError on unrecognized fields.
        """
        ...

    def apply_diff(self, diff: TimelineDiff) -> None:
        """
        Apply a precomputed TimelineDiff.
        """
        for address in diff.to_remove:
            self.remove(address)
        for old, new in diff.to_replace:
            self.replace(old, new)
        for address in diff.to_add:
            self.add(address)


class TravelRepository(ABC):

    VALID_FIELDS = {"origin", "destination", "date", "notes"}

    @abstractmethod
    def list(self) -> List[Travel]: ...

    @abstractmethod
    def add(self, travel: Travel) -> None:
        """
        Add a new travel record.
        Raises ValueError if it already exists.
        """
        ...

    @abstractmethod
    def remove(self, travel: Travel) -> None:
        """
        Remove a travel record.
        Raises ValueError if it does not exist.
        """
        ...

    @abstractmethod
    def replace(self, old: Travel, new: Travel) -> None:
        """
        Replace old with new. Raises ValueError if old does not exist.
        """
        ...

    @abstractmethod
    def find(self, **filters) -> List[Travel]:
        """
        Return all travel records matching the given filters.
        Omitting a field means do not filter on that field.
        Passing None for a field means matching on NULL.
        Raises ValueError on unrecognized fields.
        """
        ...
