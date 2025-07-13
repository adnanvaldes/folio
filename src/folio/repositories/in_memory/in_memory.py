from typing import Dict, Optional, List
from ..base import Repository, R


class InMemoryRepository(Repository[R]):
    def __init__(self):
        self._storage: Dict[int, R] = {}
        self._next_id: int = 1

    def add(self, record: R) -> int:
        """
        Add a new record to the repository and return its assigned ID
        """
        for existing_record in self._storage.values():
            if existing_record == record:
                raise ValueError("Duplicate entry")

        record_id = self._next_id
        self._storage[record_id] = record
        self._next_id += 1
        return record_id

    def delete(self, id: int) -> Optional[R]:
        """
        Delete a record by its repository-assigned ID and return the delete drecord
        """
        return self._storage.pop(id, None)

    def get(self, id: int) -> Optional[R]:
        """
        Retrieve a record by its repository-assigned ID
        """
        return self._storage.get(id)
