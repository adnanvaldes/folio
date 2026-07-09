import datetime as dt

from folio.models.employment import Employment
from folio.services import EmploymentService
from folio.uow import EmploymentSQLiteUoW

from .output import print_item, print_list
from .interactive import prompt_field, confirm, print_record


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("company", old.company),
            ("start", old.start),
            ("end", old.end),
            ("supervisor", old.supervisor),
            ("address", old.address),
            ("phone", old.phone),
        ]
    )
    print()
    company = prompt_field("company", old.company)
    start = prompt_field("start", old.start, _parse_date)
    end = prompt_field("end", old.end, _parse_date)
    supervisor = prompt_field("supervisor", old.supervisor)
    address = prompt_field("address", old.address)
    phone = prompt_field("phone", old.phone)
    new = Employment(
        company=company,
        start=start,
        end=end,
        supervisor=supervisor,
        address=address,
        phone=phone,
    )
    print()
    print_record(
        [
            ("company", new.company),
            ("start", new.start),
            ("end", new.end),
            ("supervisor", new.supervisor),
            ("address", new.address),
            ("phone", new.phone),
        ]
    )
    if not confirm():
        raise ValueError("Cancelled")
    return new


def setup(parser):
    ap = parser.add_parser("add", help="Add an employment record")
    ap.add_argument("company")
    ap.add_argument("start", help="ISO-8601 date")
    ap.add_argument("--end", default=None, help="ISO-8601 date (omit if current)")
    ap.add_argument("--supervisor", required=True)
    ap.add_argument("--address", required=True)
    ap.add_argument("--phone", required=True)

    lp = parser.add_parser("list", help="List all employment records")

    fp = parser.add_parser("find", help="Search employment records")
    fp.add_argument("--company", default=None)
    fp.add_argument("--start", default=None)
    fp.add_argument("--end", default=None)
    fp.add_argument("--supervisor", default=None)
    fp.add_argument("--address", default=None)
    fp.add_argument("--phone", default=None)

    rmp = parser.add_parser("remove", help="Remove an employment record")
    rmp.add_argument("company")
    rmp.add_argument("start")

    rep = parser.add_parser("replace", help="Replace an employment record")
    rep.add_argument("company")
    rep.add_argument("start")
    rep.add_argument("--new-company", default=None, dest="new_company")
    rep.add_argument("--new-start", default=None, dest="new_start")
    for dest in ("end", "supervisor", "address", "phone"):
        rep.add_argument(f"--{dest.replace('_', '-')}", default=None, dest=dest)


def _parse_date(s):
    if s is None:
        return None
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
    uow = EmploymentSQLiteUoW(args.db_path)
    svc = EmploymentService(uow)
    obj = Employment(
        company=args.company,
        start=_parse_date(args.start),
        supervisor=args.supervisor,
        address=args.address,
        phone=args.phone,
        end=_parse_date(args.end),
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    uow = EmploymentSQLiteUoW(args.db_path)
    svc = EmploymentService(uow)
    items = svc.list()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = EmploymentSQLiteUoW(args.db_path)
    svc = EmploymentService(uow)
    filters = {}
    for key in ("company", "supervisor", "address", "phone"):
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
    uow = EmploymentSQLiteUoW(args.db_path)
    svc = EmploymentService(uow)
    obj = _find_one(svc, company=args.company, start=_parse_date(args.start))
    svc.remove(obj)
    print_item(obj, args.json, label="Removed")


@handler("replace")
def _replace(args):
    uow = EmploymentSQLiteUoW(args.db_path)
    svc = EmploymentService(uow)
    old = _find_one(svc, company=args.company, start=_parse_date(args.start))
    has_new = any(
        getattr(args, f"new_{f}", None) is not None for f in ("company", "start")
    )
    if has_new:
        new = Employment(
            company=args.new_company if args.new_company is not None else old.company,
            start=(
                _parse_date(args.new_start) if args.new_start is not None else old.start
            ),
            supervisor=(
                args.supervisor if args.supervisor is not None else old.supervisor
            ),
            address=args.address if args.address is not None else old.address,
            phone=args.phone if args.phone is not None else old.phone,
            end=_parse_date(args.end) if args.end is not None else old.end,
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
