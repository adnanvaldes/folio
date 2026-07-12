import datetime as dt
from collections.abc import Callable

from folio.exceptions import (
    FolioAmbiguousQueryError,
    FolioNotFoundError,
    FolioParseError,
)


def parse_date(s):
    if s is None:
        return None
    return dt.date.fromisoformat(s)


def parse_bool(s):
    if s.lower() in ("yes", "true", "1", "y"):
        return True
    if s.lower() in ("no", "false", "0", "n"):
        return False
    raise FolioParseError(f"Invalid boolean: '{s}' (expected yes/no/true/false/1/0)")


HANDLERS: dict[str, Callable] = {}


def handler(action):
    def wrap(fn):
        HANDLERS[action] = fn
        return fn

    return wrap


def find_one(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise FolioNotFoundError("Record not found")
    if len(results) > 1:
        raise FolioAmbiguousQueryError(f"Expected one record, found {len(results)}")
    return results[0]
