from importlib.metadata import PackageNotFoundError, version

from folio.exceptions import (
    FolioAmbiguousQueryError as FolioAmbiguousQueryError,
)
from folio.exceptions import (
    FolioCancelledError as FolioCancelledError,
)
from folio.exceptions import (
    FolioCascadeError as FolioCascadeError,
)
from folio.exceptions import (
    FolioDuplicateError as FolioDuplicateError,
)
from folio.exceptions import (
    FolioError as FolioError,
)
from folio.exceptions import (
    FolioInvalidFilterError as FolioInvalidFilterError,
)
from folio.exceptions import (
    FolioNotFoundError as FolioNotFoundError,
)
from folio.exceptions import (
    FolioParseError as FolioParseError,
)
from folio.exceptions import (
    FolioStateConflictError as FolioStateConflictError,
)
from folio.exceptions import (
    FolioTimelineError as FolioTimelineError,
)
from folio.exceptions import (
    FolioValidationError as FolioValidationError,
)

try:
    __version__ = version("folio")
except PackageNotFoundError:
    __version__ = "1.1.0"
