from collections.abc import Callable

from folio.exceptions import FolioCancelledError, FolioValidationError
from folio.models import Work
from folio.services import WorkService

from .common import find_one, make_work_uow, parse_bool
from .interactive import confirm, print_record, prompt_field
from .output import print_item, print_list

_HANDLERS: dict[str, Callable] = {}


def handler(action: str):
    def wrap(fn):
        _HANDLERS[action] = fn
        return fn

    return wrap


def _interactive_replace(old):
    print("\nCurrent record:")
    print_record(
        [
            ("author", old.author),
            ("title", old.title),
            ("year", old.year),
            ("genre", old.genre),
            ("is_read", "Yes" if old.is_read else "No"),
        ]
    )
    print()
    author = prompt_field("author", old.author)
    title = prompt_field("title", old.title)
    year = prompt_field("year", old.year, int)
    genre = prompt_field("genre", old.genre)
    raw = prompt_field("is_read", "Yes" if old.is_read else "No")
    is_read = parse_bool(raw)
    new = Work(author=author, title=title, year=year, genre=genre, is_read=is_read)
    print()
    print_record(
        [
            ("author", new.author),
            ("title", new.title),
            ("year", new.year),
            ("genre", new.genre),
            ("is_read", "Yes" if new.is_read else "No"),
        ]
    )
    if not confirm():
        raise FolioCancelledError("Cancelled")
    return new


def setup(parser):
    ap = parser.add_parser("add", help="Add a work")
    ap.add_argument("author")
    ap.add_argument("title")
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--genre", default=None)
    ap.add_argument("--is-read", default="no", dest="is_read")

    parser.add_parser("show", help="Show all works")

    fp = parser.add_parser("find", help="Search works")
    fp.add_argument("--author", default=None)
    fp.add_argument("--title", default=None)
    fp.add_argument("--year", type=int, default=None)
    fp.add_argument("--genre", default=None)
    fp.add_argument("--is-read", default=None, dest="is_read")
    fp.add_argument(
        "--before", type=int, default=None, metavar="YEAR", help="Year before"
    )
    fp.add_argument(
        "--after", type=int, default=None, metavar="YEAR", help="Year after"
    )
    fp.add_argument("--contains", default=None, metavar="TEXT", help="Substring match")

    rmp = parser.add_parser("remove", help="Remove a work")
    rmp.add_argument("author")
    rmp.add_argument("title")
    rmp.add_argument("--year", type=int, default=None)
    rmp.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Remove associated books too",
    )

    up = parser.add_parser("update", help="Update genre and/or read status")
    up.add_argument("author")
    up.add_argument("title")
    up.add_argument("--year", type=int, default=None)
    up.add_argument("--genre", default=None)
    up.add_argument("--is-read", default=None, dest="is_read")

    rep = parser.add_parser(
        "replace", help="Replace a work (change genre/is_read or identity)"
    )
    rep.add_argument("author")
    rep.add_argument("title")
    rep.add_argument("--year", type=int, default=None)
    rep.add_argument("--new-author", default=None, dest="new_author")
    rep.add_argument("--new-title", default=None, dest="new_title")
    rep.add_argument("--new-year", type=int, default=None, dest="new_year")
    rep.add_argument("--genre", default=None)
    rep.add_argument("--is-read", default=None, dest="is_read")


@handler("add")
def _add(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    obj = Work(
        author=args.author,
        title=args.title,
        year=args.year,
        genre=args.genre,
        is_read=parse_bool(args.is_read),
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("show")
def _show(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    items = svc.list_all()
    print_list(items, args.json)


@handler("find")
def _find(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    filters = {}
    for key in ("author", "title", "genre"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = val
    if args.year is not None:
        filters["year"] = args.year
    if args.is_read is not None:
        filters["is_read"] = parse_bool(args.is_read)
    if args.before is not None:
        filters["year__before"] = args.before
    if args.after is not None:
        filters["year__after"] = args.after
    if args.contains is not None:
        for field in ("author", "title", "genre"):
            filters[f"{field}__contains"] = args.contains
    items = svc.find(**filters)
    print_list(items, args.json)


@handler("remove")
def _remove(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    obj = find_one(svc, author=args.author, title=args.title, year=args.year)
    svc.remove(obj, force=args.force)
    print_item(obj, args.json, label="Removed")


@handler("update")
def _update(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    old = find_one(svc, author=args.author, title=args.title, year=args.year)
    kwargs = {}
    if args.genre is not None:
        kwargs["genre"] = args.genre
    if args.is_read is not None:
        kwargs["is_read"] = parse_bool(args.is_read)
    if not kwargs:
        raise FolioValidationError("No fields to update (use --genre and/or --is-read)")
    svc.update(old, **kwargs)
    updated = find_one(svc, author=args.author, title=args.title, year=args.year)
    print_item(updated, args.json, label="Updated")


@handler("replace")
def _replace(args):
    uow = make_work_uow(args.db_path)
    svc = WorkService(uow)
    old = find_one(svc, author=args.author, title=args.title, year=args.year)
    has_new = any(
        getattr(args, f"new_{f}", None) is not None for f in ("author", "title", "year")
    )
    if has_new:
        new = Work(
            author=args.new_author if args.new_author is not None else old.author,
            title=args.new_title if args.new_title is not None else old.title,
            year=args.new_year if args.new_year is not None else old.year,
            genre=args.genre if args.genre is not None else old.genre,
            is_read=(
                parse_bool(args.is_read) if args.is_read is not None else old.is_read
            ),
        )
    else:
        new = _interactive_replace(old)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
