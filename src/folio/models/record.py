from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, TypeVar, Type

from folio.models.common import ValidationResult


class Record[Self: "Record"](ABC):
    """
    Abstract base class for all records
    """

    @abstractmethod
    def validate(self) -> ValidationResult:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass
