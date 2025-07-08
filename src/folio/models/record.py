from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, TypeVar, Type

from folio.models.common import ValidationResult
from folio.services.protocols import Validator, Formatter
from folio.services.serializers import SerializeStrategy

R = TypeVar("R", bound="Record")
O = TypeVar("O")


class Record[R: "Record"](ABC):
    """
    Abstract base class for all records
    """

    @classmethod
    def deserialize(cls: R, data: O, serializer: SerializeStrategy[R]) -> R:
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

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __eq__(self) -> bool: ...

    @abstractmethod
    def __hash__(self) -> hash: ...
