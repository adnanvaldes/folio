import datetime as dt
from collections.abc import Callable

from folio.models import Travel
from folio.services import TravelService
from folio.uow import TravelSQLiteUoW

from .interactive import confirm, print_record, prompt_field
from .output import print_item, print_list


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("origin", old.origin),
            ("destination", old.destination),
            ("date", old.date),
            ("note", old.note),
        ]
    )
    print()
    origin = prompt_field("origin", old.origin)
    destination = prompt_field("destination", old.destination)
    date = prompt_field("date", old.date, _parse_date)
    note = prompt_field("note", old.note)
    new = Travel(origin=origin, destination=destination, date=date, note=note)
    print()
    print_record(
        [
            ("origin", new.origin),
            ("destination", new.destination),
            ("date", new.date),
            ("note", new.note),
        ]
    )
    if not confirm():
        raise ValueError("Cancelled")
    return new


def setup(parser):
    ap = parser.add_parser("add", help="Add a travel record")
    ap.add_argument("origin", help="3-letter origin country code")
    ap.add_argument("destination", help="3-letter destination country code")
    ap.add_argument("date", help="ISO-8601 date (YYYY-MM-DD)")
    ap.add_argument("--note", default="", help="Optional note")

    parser.add_parser("list", help="List all travel records")

    fp = parser.add_parser("find", help="Search travel records")
    fp.add_argument("--origin", default=None)
    fp.add_argument("--destination", default=None)
    fp.add_argument("--date", default=None)
    fp.add_argument("--note", default=None)

    rmp = parser.add_parser("remove", help="Remove a travel record")
    rmp.add_argument("origin")
    rmp.add_argument("destination")
    rmp.add_argument("date")

    rep = parser.add_parser("replace", help="Replace a travel record")
    rep.add_argument("origin")
    rep.add_argument("destination")
    rep.add_argument("date")
    rep.add_argument("--new-origin", default=None, dest="new_origin")
    rep.add_argument("--new-destination", default=None, dest="new_destination")
    rep.add_argument("--new-date", default=None, dest="new_date")
    rep.add_argument("--new-note", default=None, dest="new_note")


def _parse_date(s):
    return dt.date.fromisoformat(s)


def _find_one(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise ValueError("Record not found")
    if len(results) > 1:
        raise ValueError(f"Expected one record, found {len(results)}")
    return results[0]


_HANDLERS: dict[str, Callable] = {}


def handler(action):
    def wrap(fn):
        _HANDLERS[action] = fn
        return fn

    return wrap


@handler("add")
def _add(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    obj = Travel(
        origin=args.origin,
        destination=args.destination,
        date=_parse_date(args.date),
        note=args.note,
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    items = svc.list_all()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    filters = {}
    for key in ("origin", "destination", "date", "note"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = _parse_date(val) if key == "date" else val
    items = svc.find(**filters)
    print_list(items, args.json)


@handler("remove")
def _remove(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    obj = _find_one(
        svc,
        origin=args.origin,
        destination=args.destination,
        date=_parse_date(args.date),
    )
    svc.remove(obj)
    print_item(obj, args.json, label="Removed")


@handler("replace")
def _replace(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    old = _find_one(
        svc,
        origin=args.origin,
        destination=args.destination,
        date=_parse_date(args.date),
    )
    has_new = (
        any(
            getattr(args, f"new_{f}", None) is not None
            for f in ("origin", "destination", "date")
        )
        or args.new_note is not None
    )
    if has_new:
        new = Travel(
            origin=args.new_origin if args.new_origin is not None else args.origin,
            destination=(
                args.new_destination
                if args.new_destination is not None
                else args.destination
            ),
            date=_parse_date(args.new_date) if args.new_date is not None else old.date,
            note=args.new_note if args.new_note is not None else old.note,
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
