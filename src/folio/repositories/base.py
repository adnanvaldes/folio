from typing import Optional, List
from abc import ABC, abstractmethod

from folio.models import Record, R


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

from folio.models.address import Address, TimelineDiff

class AddressRepository(ABC):

    VALID_FIELDS = {
        "street",
        "city",
        "province",
        "country",
        "postal_code",
        "start",
        "end"
    }

    @abstractmethod
    def list(self) -> list[Address]:
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

    @abstractmehod
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

    @absractmethod
    def find(self, **filters) -> list[Address]:
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
