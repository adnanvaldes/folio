from typing import Dict, Optional
from .base import Repository, R


class InMemoryRepository(Repository[R]):
    def __init__(self):
        self._storage: Dict[int, R] = {}
        self._next_id: int = 1
        self._record_hashes: set[int] = set()

    def add(self, record: R) -> int:
        """
        Add a new record to the repository and return its assigned ID
        """
        record_hash = hash(record)
        if record_hash in self._record_hashes:
            for existing_record in self._storage.values():
                if existing_record == record:
                    raise ValueError("Duplicate entry")

        record_id = self._next_id
        self._storage[record_id] = record
        self._record_hashes.add(record_hash)
        self._next_id += 1
        return record_id

    def get(self, id: int) -> Optional[R]:
        """
        Retrieve a record by its repository-assigned ID
        """
        return self._storage.get(id)

    def list(self):
        """
        Return a list with all records in repository
        """
        return list(self._storage.values())
