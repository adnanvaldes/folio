from typing import List, Optional, Callable
from abc import ABC, abstractmethod

from folio.models.record import Record


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


class InMemoryRepository(Repository[R]):
    def __init__(self):
        self._storage: Dict[int, R] = {}

    def _make_key(self, record: R) -> int:
        """
        Generate a unique key for the Record
        using __hash__
        """
        return hash(record)

    def add(self, record: R) -> int:
        """
        Add a new record to the repository and return its assigned ID
        """
        key = self._make_key(record)
        if key in self._storage:
            raise ValueError("Duplicate entry")
        self_storage[key] = record
        return key

    def get(self, id: int) -> Optional[R]:
        """
        Retrieve a record by its repository-assigned ID
        """
        return self._storage.get[id]
