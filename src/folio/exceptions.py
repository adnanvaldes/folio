class FolioError(Exception):
    """Base exception for all folio domain errors."""


class FolioNotFoundError(FolioError):
    """Raised when a record lookup fails."""


class FolioDuplicateError(FolioError):
    """Raised when adding a record that already exists."""


class FolioValidationError(FolioError):
    """Raised when input data fails model validation."""


class FolioStateConflictError(FolioError):
    """Raised when an operation is invalid on the current state."""


class FolioTimelineError(FolioError):
    """Raised for address timeline conflicts."""


class FolioCascadeError(FolioError):
    """Raised when a cascading delete is blocked."""


class FolioAmbiguousQueryError(FolioError):
    """Raised when find() returns multiple results but one was expected."""


class FolioInvalidFilterError(FolioError):
    """Raised when an unknown filter field is passed to find()."""


class FolioCancelledError(FolioError):
    """Raised when the user cancels an interactive operation."""


class FolioParseError(FolioError):
    """Raised when CLI input cannot be parsed."""
