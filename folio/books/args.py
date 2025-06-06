# books/args.py

from typing import Annotated, Optional
from typer import Option

from books.schemas import BookFormat


# Shared argument definitions

title = Annotated[
    str, Option("--title", "-t", help="Title of the work", show_default=False)
]
author = Annotated[
    str, Option("--author", "-a", help="Author of the work", show_default=False)
]
year = Annotated[
    int,
    Option(
        "--year", "-y", help="Year written (use negative for BCE)", show_default=False
    ),
]
genre = Annotated[
    str, Option("--genre", "-g", help="Genre of the work", show_default=False)
]
is_read = Annotated[
    bool,
    Option(
        "--is-read/--no-read", "-r/-R", help="Filter by read status", show_default=False
    ),
]

pages = Annotated[
    int, Option("--pages", "-p", help="Number of pages", show_default=False)
]
format = Annotated[
    BookFormat,
    Option(
        "--format",
        "-f",
        case_sensitive=False,
        help="Format/medium of the book",
        show_default=False,
    ),
]
isbn = Annotated[
    str, Option("--isbn", "-i", help="ISBN-13 of the book", show_default=False)
]


class CreateArgs:
    title = title
    author = author
    year = year
    genre = genre
    is_read = is_read

    pages = pages
    format = format
    isbn = isbn

    add_book = Annotated[bool, Option(help="Associate work with book in database")]


class SearchArgs:
    title = title
    author = author
    year = year
    genre = genre
    is_read = is_read

    pages = pages
    format = format
    isbn = isbn

    year_min = Annotated[
        Optional[int],
        Option(
            "--year-from", "-yf", help="Start year for range search", show_default=False
        ),
    ]
    year_max = Annotated[
        Optional[int],
        Option(
            "--year-to", "-yt", help="End year for range search", show_default=False
        ),
    ]
    pages_min = Annotated[
        Optional[int],
        Option(
            "--pages-min", "-pf", help="Minimum number of pages", show_default=False
        ),
    ]
    pages_max = Annotated[
        Optional[int],
        Option(
            "--pages-max", "-pt", help="Maximum number of pages", show_default=False
        ),
    ]
    work_id = Annotated[
        Optional[int],
        Option(
            "--work-id", "-wid", help="ID of the work in database", show_default=False
        ),
    ]
    book_id = Annotated[
        Optional[int],
        Option(
            "--book-id", "-bid", help="ID of the book in database", show_default=False
        ),
    ]
    limit = Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Maximum number of results to display",
            show_default=False,
        ),
    ]

    _return_session = Annotated[bool, Option(hidden=True)]


class UpdateArgs:
    set_title = Annotated[
        str, Option("--set-title", "-st", help="Set new title", show_default=False)
    ]
    set_author = Annotated[
        str, Option("--set-author", "-sa", help="Set new author", show_default=False)
    ]
    set_year = Annotated[
        int, Option("--set-year", "-sy", help="Set new year", show_default=False)
    ]
    set_genre = Annotated[
        str, Option("--set-genre", "-sg", help="Set new genre", show_default=False)
    ]
    set_is_read = Annotated[
        bool,
        Option(
            "--set-is-read/--set-no-read",
            "-sr/-SR",
            help="Set new read status",
            show_default=False,
        ),
    ]
    set_pages = Annotated[
        int, Option("--set-pages", "-sp", help="Set new page count", show_default=False)
    ]
    set_format = Annotated[
        BookFormat,
        Option(
            "--set-format",
            "-sf",
            case_sensitive=False,
            help="Set new format",
            show_default=False,
        ),
    ]
    set_isbn = Annotated[
        str, Option("--set-isbn", "-si", help="Set new ISBN-13", show_default=False)
    ]
