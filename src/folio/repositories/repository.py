from typing import List
from abc import ABC, abstractmethod


class Repository[R: Record](ABC):
    @abstractmethod
    def add(self, record: R) -> None: ...

    @abstractmethod
    def get(self, record_id: int) -> R: ...

    @abstractmethod
    def list(self) -> List[R]: ...

    @abstractmethod
    def delete(self, record_id: int) -> None: ...


class InMemoryRepository[R: Record](Repository[R]):
    def __init__(self):
        self._data: dict[int, R] = {}
        self._next_id: int = 1

    def add(self, record: R) -> None:
        """
        Add a record to the repository. Assigns an ID if it doesn't have one
        #TODO: Consider the case when an existing ID is passed.
        """
        validation = record.validate()
        if not validation.is_valid:
            raise ValueError(f"Invalid record: {', '.join(validation.errors)}")

        if record.id is None:
            record.id = self._next_id
            self._next_id += 1

        self._data[record.id] = record

    def get(self, record_id: int) -> R:
        """
        Retrieve a record by ID. Raises KeyError if not found
        """
        if record_id not in self._data:
            raise KeyError(f"Reord with ID {record_id} not found")
        return self._data[record_id]

    def list(self) -> List[R]:
        """
        Return all records as a list
        """
        return list(self._data.values())

    def delete(self, record_id: int) -> None:
        """
        Delete a record by ID. Raises KeyError if not found.
        """
        if record_id not in self._data:
            raise KeyError(f"Record with ID {record_id} not found")
        del self._data[record_id]
