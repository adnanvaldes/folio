from folio.models.book import Book, FormatType
from folio.models.work import Work
from folio.services import BookService, WorkService
from folio.uow import BookSQLiteUoW, WorkSQLiteUoW

from .output import print_item, print_list
from .interactive import prompt_field, confirm, print_record


def _parse_bool(s):
    if s.lower() in ("yes", "true", "1", "y"):
        return True
    if s.lower() in ("no", "false", "0", "n"):
        return False
    raise ValueError(f"Invalid boolean: '{s}' (expected yes/no/true/false/1/0)")


def _parse_format(s):
    return FormatType(s.lower())


def _interactive_replace(old, work_svc):
    work = old.work
    print("\nCurrent record:")
    print_record(
        [
            ("author", work.author),
            ("title", work.title),
            ("year", work.year),
            ("format", old.format_type.value),
            ("isbn", old.isbn),
            ("pages", old.pages),
            ("duration_minutes", old.duration_minutes),
            ("narrator", old.narrator),
        ]
    )
    print()
    author = prompt_field("author", work.author)
    title = prompt_field("title", work.title)
    year = prompt_field("year", work.year, int)
    fmt_raw = prompt_field("format", old.format_type.value)
    fmt = (
        _parse_format(fmt_raw) if fmt_raw != old.format_type.value else old.format_type
    )
    isbn = prompt_field("isbn", old.isbn)
    pages = prompt_field("pages", old.pages, int)
    duration = prompt_field("duration_minutes", old.duration_minutes, int)
    narrator = prompt_field("narrator", old.narrator)
    new_work = Work(
        author=author,
        title=title,
        year=year,
        genre=work.genre,
        is_read=work.is_read,
    )
    new = Book(
        work=new_work,
        format_type=fmt,
        isbn=isbn or None,
        pages=pages,
        duration_minutes=duration,
        narrator=narrator or None,
    )
    print()
    print_record(
        [
            ("author", new.work.author),
            ("title", new.work.title),
            ("year", new.work.year),
            ("format", new.format_type.value),
            ("isbn", new.isbn),
            ("pages", new.pages),
            ("duration_minutes", new.duration_minutes),
            ("narrator", new.narrator),
        ]
    )
    if not confirm():
        raise ValueError("Cancelled")
    return new


def _find_one_work(service, **kwargs):
    results = service.find(**kwargs)
    if not results:
        raise ValueError("Work not found")
    if len(results) > 1:
        raise ValueError(f"Expected one work, found {len(results)}")
    return results[0]


def setup(parser):
    ap = parser.add_parser("add", help="Add a book")
    ap.add_argument("author")
    ap.add_argument("title")
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--format", required=True, choices=["print", "ebook", "audio"])
    ap.add_argument("--pages", type=int, default=None)
    ap.add_argument(
        "--duration-minutes", type=int, default=None, dest="duration_minutes"
    )
    ap.add_argument("--isbn", default=None)
    ap.add_argument("--narrator", default=None)
    ap.add_argument("--is-read", default="no", dest="is_read")

    lp = parser.add_parser("list", help="List all books")

    fp = parser.add_parser("find", help="Search books")
    fp.add_argument("--author", default=None)
    fp.add_argument("--title", default=None)
    fp.add_argument("--year", type=int, default=None)
    fp.add_argument("--format", default=None)
    fp.add_argument("--isbn", default=None)
    fp.add_argument("--narrator", default=None)

    rmp = parser.add_parser("remove", help="Remove a book")
    rmp.add_argument("author")
    rmp.add_argument("title")
    rmp.add_argument("--year", type=int, default=None)
    rmp.add_argument("--format", required=True)
    rmp.add_argument("--isbn", default="")

    rep = parser.add_parser("replace", help="Replace a book record")
    rep.add_argument("author")
    rep.add_argument("title")
    rep.add_argument("--year", type=int, default=None)
    rep.add_argument("--format", required=True)
    rep.add_argument("--isbn", default="")
    rep.add_argument("--new-author", default=None, dest="new_author")
    rep.add_argument("--new-title", default=None, dest="new_title")
    rep.add_argument("--new-year", type=int, default=None, dest="new_year")
    rep.add_argument("--new-isbn", default=None, dest="new_isbn")
    rep.add_argument("--new-format", default=None, dest="new_format")
    rep.add_argument("--new-pages", type=int, default=None, dest="new_pages")
    rep.add_argument(
        "--new-duration-minutes", type=int, default=None, dest="new_duration_minutes"
    )
    rep.add_argument("--new-narrator", default=None, dest="new_narrator")


_HANDLERS = {}


def handler(action):
    def wrap(fn):
        _HANDLERS[action] = fn
        return fn

    return wrap


def _make_work(author, title, year, is_read=False):
    return Work(author=author, title=title, year=year, genre=None, is_read=is_read)


@handler("add")
def _add(args):
    book_uow = BookSQLiteUoW(args.db_path)
    svc = BookService(book_uow)
    work = _make_work(args.author, args.title, args.year, _parse_bool(args.is_read))
    fmt = _parse_format(args.format)
    obj = Book(
        work=work,
        format_type=fmt,
        isbn=args.isbn,
        pages=args.pages,
        duration_minutes=args.duration_minutes,
        narrator=args.narrator,
    )
    svc.add(obj)
    print_item(obj, args.json)


@handler("list")
def _list(args):
    svc = BookService(BookSQLiteUoW(args.db_path))
    items = svc.list()
    print_list(items, args.json)


@handler("find")
def _find(args):
    svc = BookService(BookSQLiteUoW(args.db_path))
    filters = {}
    for key in ("author", "title"):
        val = getattr(args, key)
        if val is not None:
            filters[key] = val
    if args.year is not None:
        filters["year"] = args.year
    if args.format is not None:
        filters["format_type"] = _parse_format(args.format).value
    if args.isbn is not None:
        filters["isbn"] = args.isbn
    if args.narrator is not None:
        filters["narrator"] = args.narrator
    items = svc.find(**filters)
    print_list(items, args.json)


@handler("remove")
def _remove(args):
    work_svc = WorkService(WorkSQLiteUoW(args.db_path))
    svc = BookService(BookSQLiteUoW(args.db_path))
    work = _find_one_work(
        work_svc, author=args.author, title=args.title, year=args.year
    )
    fmt = _parse_format(args.format)
    isbn = args.isbn or None
    results = svc.find(
        author=work.author,
        title=work.title,
        year=work.year,
        format_type=fmt.value,
        isbn=isbn,
    )
    if not results:
        raise ValueError("Book not found")
    obj = results[0]
    svc.remove(obj)
    print_item(obj, args.json, label="Removed")


@handler("replace")
def _replace(args):
    work_svc = WorkService(WorkSQLiteUoW(args.db_path))
    svc = BookService(BookSQLiteUoW(args.db_path))
    work = _find_one_work(
        work_svc, author=args.author, title=args.title, year=args.year
    )
    fmt = _parse_format(args.format)
    isbn = args.isbn or None
    results = svc.find(
        author=work.author,
        title=work.title,
        year=work.year,
        format_type=fmt.value,
        isbn=isbn,
    )
    if not results:
        raise ValueError("Book not found")
    old = results[0]
    has_new = any(
        getattr(args, f"new_{f}", None) is not None
        for f in (
            "author",
            "title",
            "year",
            "isbn",
            "format",
            "pages",
            "duration_minutes",
            "narrator",
        )
    )
    if has_new:
        new_work = Work(
            author=args.new_author if args.new_author is not None else work.author,
            title=args.new_title if args.new_title is not None else work.title,
            year=args.new_year if args.new_year is not None else work.year,
            genre=work.genre,
            is_read=work.is_read,
        )
        new_fmt = _parse_format(args.new_format) if args.new_format else old.format_type
        new_isbn = args.new_isbn if args.new_isbn is not None else old.isbn
        new = Book(
            work=new_work,
            format_type=new_fmt,
            isbn=new_isbn,
            pages=args.new_pages if args.new_pages is not None else old.pages,
            duration_minutes=(
                args.new_duration_minutes
                if args.new_duration_minutes is not None
                else old.duration_minutes
            ),
            narrator=(
                args.new_narrator if args.new_narrator is not None else old.narrator
            ),
        )
    else:
        new = _interactive_replace(old, work_svc)
    svc.replace(old, new)
    print_item(new, args.json, label="Replaced with")
