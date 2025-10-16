class DomainError(Exception):
    """Base class for domain-level errors"""


class DuplicateRecordError(DomainError):
    """Raised when attempting to isnert a recors that already exists."""
