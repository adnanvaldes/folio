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
