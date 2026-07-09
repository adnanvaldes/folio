import datetime as dt

from folio.models.travel import Travel
from folio.services import TravelService
from folio.uow import TravelSQLiteUoW

from .output import print_item, print_list
from .interactive import prompt_field, confirm, print_record


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("origin", old.origin),
            ("destination", old.destination),
            ("date", old.date),
            ("notes", old.notes),
        ]
    )
    print()
    origin = prompt_field("origin", old.origin)
    destination = prompt_field("destination", old.destination)
    date = prompt_field("date", old.date, _parse_date)
    notes = prompt_field("notes", old.notes)
    new = Travel(origin=origin, destination=destination, date=date, notes=notes)
    print()
    print_record(
        [
            ("origin", new.origin),
            ("destination", new.destination),
            ("date", new.date),
            ("notes", new.notes),
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
    ap.add_argument("--notes", default="", help="Optional notes")

    rp = parser.add_parser("list", help="List all travel records")

    fp = parser.add_parser("find", help="Search travel records")
    fp.add_argument("--origin", default=None)
    fp.add_argument("--destination", default=None)
    fp.add_argument("--date", default=None)
    fp.add_argument("--notes", default=None)

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
    rep.add_argument("--notes", default=None)


def _parse_date(s):
    return dt.date.fromisoformat(s)


def _find_one(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise ValueError("Record not found")
    if len(results) > 1:
        raise ValueError(f"Expected one record, found {len(results)}")
    return results[0]


_HANDLERS = {}


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
        notes=args.notes,
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    items = svc.list()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = TravelSQLiteUoW(args.db_path)
    svc = TravelService(uow)
    filters = {}
    for key in ("origin", "destination", "date", "notes"):
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
        or args.notes is not None
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
            notes=args.notes if args.notes is not None else old.notes,
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
