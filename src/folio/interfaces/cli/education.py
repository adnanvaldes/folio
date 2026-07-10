import datetime as dt
from collections.abc import Callable

from folio.exceptions import (
    FolioAmbiguousQueryError,
    FolioCancelledError,
    FolioNotFoundError,
)
from folio.models import Education
from folio.services import EducationService
from folio.uow import EducationSQLiteUoW

from .interactive import confirm, print_record, prompt_field
from .output import print_item, print_list


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("field", old.field),
            ("start", old.start),
            ("end", old.end),
            ("school", old.school),
            ("city", old.city),
            ("country", old.country),
            ("credential", old.credential),
        ]
    )
    print()
    field = prompt_field("field", old.field)
    start = prompt_field("start", old.start, _parse_date)
    end = prompt_field("end", old.end, _parse_date)
    school = prompt_field("school", old.school)
    city = prompt_field("city", old.city)
    country = prompt_field("country", old.country)
    credential = prompt_field("credential", old.credential)
    new = Education(
        field=field,
        start=start,
        end=end,
        school=school,
        city=city,
        country=country,
        credential=credential,
    )
    print()
    print_record(
        [
            ("field", new.field),
            ("start", new.start),
            ("end", new.end),
            ("school", new.school),
            ("city", new.city),
            ("country", new.country),
            ("credential", new.credential),
        ]
    )
    if not confirm():
        raise FolioCancelledError("Cancelled")
    return new


def setup(parser):
    ap = parser.add_parser("add", help="Add an education record")
    ap.add_argument("field", help="Field of study")
    ap.add_argument("start", help="ISO-8601 date")
    ap.add_argument("end", help="ISO-8601 date")
    ap.add_argument("school", help="School or institution name")
    ap.add_argument("city", help="City")
    ap.add_argument("country", help="Country")
    ap.add_argument("credential", help="Credential type (e.g. Certificate)")

    parser.add_parser("list", help="List all education records")

    fp = parser.add_parser("find", help="Search education records")
    fp.add_argument("--field", default=None)
    fp.add_argument("--start", default=None)
    fp.add_argument("--end", default=None)
    fp.add_argument("--school", default=None)
    fp.add_argument("--city", default=None)
    fp.add_argument("--country", default=None)
    fp.add_argument("--credential", default=None)
    fp.add_argument("--before", default=None, metavar="DATE", help="Start before date")
    fp.add_argument("--after", default=None, metavar="DATE", help="Start after date")
    fp.add_argument("--contains", default=None, metavar="TEXT", help="Substring match")

    rmp = parser.add_parser("remove", help="Remove an education record")
    rmp.add_argument("field")
    rmp.add_argument("start")
    rmp.add_argument("end")
    rmp.add_argument("school")
    rmp.add_argument("city")
    rmp.add_argument("country")
    rmp.add_argument("credential")

    rep = parser.add_parser("replace", help="Replace an education record")
    rep.add_argument("field")
    rep.add_argument("start")
    rep.add_argument("end")
    rep.add_argument("school")
    rep.add_argument("city")
    rep.add_argument("country")
    rep.add_argument("credential")
    for dest in (
        "new_field",
        "new_start",
        "new_end",
        "new_school",
        "new_city",
        "new_country",
        "new_credential",
    ):
        rep.add_argument(f"--{dest.replace('_', '-')}", default=None, dest=dest)


def _parse_date(s):
    if s is None:
        return None
    return dt.date.fromisoformat(s)


def _find_one(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise FolioNotFoundError("Record not found")
    if len(results) > 1:
        raise FolioAmbiguousQueryError(f"Expected one record, found {len(results)}")
    return results[0]


_HANDLERS: dict[str, Callable] = {}


def handler(action):
    def wrap(fn):
        _HANDLERS[action] = fn
        return fn

    return wrap


def _make_edu(**kwargs):
    return Education(
        field=kwargs["field"],
        start=kwargs["start"],
        end=kwargs["end"],
        school=kwargs["school"],
        city=kwargs["city"],
        country=kwargs["country"],
        credential=kwargs["credential"],
    )


@handler("add")
def _add(args):
    uow = EducationSQLiteUoW(args.db_path)
    svc = EducationService(uow)
    obj = _make_edu(
        field=args.field,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        school=args.school,
        city=args.city,
        country=args.country,
        credential=args.credential,
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    uow = EducationSQLiteUoW(args.db_path)
    svc = EducationService(uow)
    items = svc.list_all()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = EducationSQLiteUoW(args.db_path)
    svc = EducationService(uow)
    filters = {}
    for key in ("field", "school", "city", "country", "credential"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = val
    for key in ("start", "end"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = _parse_date(val)
    if args.before is not None:
        filters["start__before"] = _parse_date(args.before)
    if args.after is not None:
        filters["start__after"] = _parse_date(args.after)
    if args.contains is not None:
        for field in ("field", "school", "city", "country", "credential"):
            filters[f"{field}__contains"] = args.contains
    items = svc.find(**filters)
    print_list(items, args.json)


@handler("remove")
def _remove(args):
    uow = EducationSQLiteUoW(args.db_path)
    svc = EducationService(uow)
    obj = _find_one(
        svc,
        field=args.field,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        school=args.school,
        city=args.city,
        country=args.country,
        credential=args.credential,
    )
    svc.remove(obj)
    print_item(obj, args.json, label="Removed")


@handler("replace")
def _replace(args):
    uow = EducationSQLiteUoW(args.db_path)
    svc = EducationService(uow)
    old = _find_one(
        svc,
        field=args.field,
        start=_parse_date(args.start),
        end=_parse_date(args.end),
        school=args.school,
        city=args.city,
        country=args.country,
        credential=args.credential,
    )
    new_fields = (
        "field",
        "start",
        "end",
        "school",
        "city",
        "country",
        "credential",
    )
    has_new = any(getattr(args, f"new_{f}", None) is not None for f in new_fields)
    if has_new:
        new = _make_edu(
            field=args.new_field if args.new_field is not None else old.field,
            start=(
                _parse_date(args.new_start) if args.new_start is not None else old.start
            ),
            end=_parse_date(args.new_end) if args.new_end is not None else old.end,
            school=args.new_school if args.new_school is not None else old.school,
            city=args.new_city if args.new_city is not None else old.city,
            country=args.new_country if args.new_country is not None else old.country,
            credential=(
                args.new_credential
                if args.new_credential is not None
                else old.credential
            ),
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
