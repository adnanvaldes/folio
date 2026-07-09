import datetime as dt
from collections.abc import Callable

from folio.models import Address
from folio.services import AddressService
from folio.uow import AddressSQLiteUoW

from .interactive import confirm, print_record, prompt_field
from .output import print_item, print_list


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("street", old.street),
            ("city", old.city),
            ("province", old.province),
            ("country", old.country),
            ("postal_code", old.postal_code),
            ("start", old.start),
            ("end", old.end),
        ]
    )
    print()
    street = prompt_field("street", old.street)
    city = prompt_field("city", old.city)
    province = prompt_field("province", old.province)
    country = prompt_field("country", old.country)
    postal_code = prompt_field("postal_code", old.postal_code)
    start = prompt_field("start", old.start, _parse_date)
    end = prompt_field("end", old.end, _parse_date)
    new = Address(
        street=street,
        city=city,
        province=province,
        country=country,
        postal_code=postal_code,
        start=start,
        end=end,
    )
    print()
    print_record(
        [
            ("street", new.street),
            ("city", new.city),
            ("province", new.province),
            ("country", new.country),
            ("postal_code", new.postal_code),
            ("start", new.start),
            ("end", new.end),
        ]
    )
    if not confirm():
        raise ValueError("Cancelled")
    return new


def setup(parser):
    ap = parser.add_parser("add", help="Add an address")
    ap.add_argument("street")
    ap.add_argument("city")
    ap.add_argument("country")
    ap.add_argument("postal_code", metavar="postal-code")
    ap.add_argument("start", help="ISO-8601 date")
    ap.add_argument("--end", default=None, help="ISO-8601 date (omit if current)")
    ap.add_argument("--province", default=None)

    parser.add_parser("list", help="List all addresses")

    fp = parser.add_parser("find", help="Search addresses")
    fp.add_argument("--street", default=None)
    fp.add_argument("--city", default=None)
    fp.add_argument("--country", default=None)
    fp.add_argument("--postal-code", default=None, dest="postal_code")
    fp.add_argument("--start", default=None)
    fp.add_argument("--end", default=None)
    fp.add_argument("--province", default=None)

    rmp = parser.add_parser("remove", help="Remove an address (see service logic)")
    rmp.add_argument("street")
    rmp.add_argument("city")
    rmp.add_argument("country")
    rmp.add_argument("postal_code", metavar="postal-code")
    rmp.add_argument("start")
    rmp.add_argument("--end", default=None)
    rmp.add_argument("--province", default=None)

    rep = parser.add_parser("replace", help="Replace an address record")
    rep.add_argument("street")
    rep.add_argument("city")
    rep.add_argument("country")
    rep.add_argument("postal_code", metavar="postal-code")
    rep.add_argument("start")
    rep.add_argument("--end", default=None)
    rep.add_argument("--province", default=None)
    for dest in (
        "new_street",
        "new_city",
        "new_country",
        "new_postal_code",
        "new_start",
        "new_end",
        "new_province",
    ):
        rep.add_argument(f"--{dest.replace('_', '-')}", default=None, dest=dest)


def _parse_date(s):
    if s is None:
        return None
    return dt.date.fromisoformat(s)


def _make_addr(**kwargs):
    return Address(
        street=kwargs["street"],
        city=kwargs["city"],
        country=kwargs["country"],
        postal_code=kwargs["postal_code"],
        start=kwargs["start"],
        end=kwargs.get("end"),
        province=kwargs.get("province"),
    )


_HANDLERS: dict[str, Callable] = {}


def handler(action):
    def wrap(fn):
        _HANDLERS[action] = fn
        return fn

    return wrap


@handler("add")
def _add(args):
    uow = AddressSQLiteUoW(args.db_path)
    svc = AddressService(uow)
    obj = _make_addr(
        street=args.street,
        city=args.city,
        country=args.country,
        postal_code=args.postal_code,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        province=args.province,
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    uow = AddressSQLiteUoW(args.db_path)
    svc = AddressService(uow)
    items = svc.list()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = AddressSQLiteUoW(args.db_path)
    svc = AddressService(uow)
    filters = {}
    for key in ("street", "city", "country", "postal_code", "province"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = val
    for key in ("start", "end"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = _parse_date(val)
    items = svc.find(**filters)
    print_list(items, args.json)


@handler("remove")
def _remove(args):
    uow = AddressSQLiteUoW(args.db_path)
    svc = AddressService(uow)
    obj = _make_addr(
        street=args.street,
        city=args.city,
        country=args.country,
        postal_code=args.postal_code,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        province=args.province,
    )
    svc.remove(obj)
    print_item(obj, args.json, label="Removed")


@handler("replace")
def _replace(args):
    uow = AddressSQLiteUoW(args.db_path)
    svc = AddressService(uow)
    old = _make_addr(
        street=args.street,
        city=args.city,
        country=args.country,
        postal_code=args.postal_code,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        province=args.province,
    )
    new_fields = (
        "street",
        "city",
        "country",
        "postal_code",
        "start",
        "end",
        "province",
    )
    has_new = any(getattr(args, f"new_{f}", None) is not None for f in new_fields)
    if has_new:
        new = _make_addr(
            street=args.new_street if args.new_street is not None else args.street,
            city=args.new_city if args.new_city is not None else args.city,
            country=args.new_country if args.new_country is not None else args.country,
            postal_code=(
                args.new_postal_code
                if args.new_postal_code is not None
                else args.postal_code
            ),
            start=(
                _parse_date(args.new_start) if args.new_start is not None else old.start
            ),
            end=_parse_date(args.new_end) if args.new_end is not None else old.end,
            province=(
                args.new_province if args.new_province is not None else old.province
            ),
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
