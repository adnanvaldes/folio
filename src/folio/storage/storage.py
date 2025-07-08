from abc import ABC, abstractclassmethod
from typing import Optional, List


class StorageBacked(ABC):
    @abstractclassmethod
    def save(self, key: str, data: str) -> None:
        """
        Store data with a key
        """
        ...

    @abstractclassmethod
    def get(self, key: str) -> Optional[str]:
        """
        Get data from storage using a key
        """
        ...
