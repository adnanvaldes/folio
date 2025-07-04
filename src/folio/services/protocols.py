from typing import Protocol, Dict, Any

from folio.models.record import Record
from folio.models.common import ValidationResult


class Serializer[Record](Protocol):
    """
    Interface for serializer logic
    """

    def to_dict(self, record: Record) -> Dict[str, Any]: ...

    def from_dict(self, data: Dict[str, Any]) -> Record: ...


class Validator[Record](Protocol):
    """
    Interface for validation logic
    """

    def validate(self, record: Record) -> ValidationResult: ...


class Formatter[Record](Protocol):
    """
    Interface for formatter logic
    """

    pass
