from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import total_ordering
from typing import Dict, Any, List, TypeVar, Type

from folio.common import ValidationResult, Validator, Formatter, SerializeStrategy

R = TypeVar("R", bound="Record")
O = TypeVar("O")


@total_ordering
@dataclass
class Record[R: "Record"](ABC):
    """
    Abstract base class for all records
    """

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def _identity_fields(self) -> tuple: ...

    @abstractmethod
    def _ordering_fields(self) -> tuple: ...

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._identity_fields() == other._identity_fields()
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._ordering_fields() < other._ordering_fields()

    def __hash__(self) -> int:
        return hash(self._identity_fields())

    @classmethod
    def deserialize(cls: Type[R], data: O, serializer: SerializeStrategy[R]) -> R:
        """
        Deserialize data into a Record using the provided serializer.
        """
        return serializer.deserialize(data, cls)

    def serialize(self, serializer: SerializeStrategy[R]) -> O:
        """
        Serialize this Record using the provided Serializer
        """
        return serializer.serialize(self)

    def validate(self, validator: Validator) -> ValidationResult:
        """
        Validate this Record using the provided Validator
        """
        return validator.validate(self)
