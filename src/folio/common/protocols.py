from typing import Dict, Any, Type
from abc import ABC, abstractmethod

from folio.common import ValidationResult


class Validator[T](ABC):
    """
    Interface for validation logic
    """

    def validate(self, record: T) -> ValidationResult: ...


class Formatter[T](ABC):
    """
    Interface for formatter logic
    """

    pass


class Serializer:
    pass
