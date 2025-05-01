from enum import Enum
from typing import Annotated, List, Optional

from typer import Argument, Option


class BookFormat(str, Enum):
    print = "print"
    ebook = "ebook"
    audio = "audiobook"


class WorkArguments:
    """Class to store argument definitions for work-related commands"""

    title = Annotated[
        str,
        Argument(help="Title of the work", show_default=False),
    ]
    author = Annotated[
        str,
        Argument(help="Author of the work", show_default=False),
    ]
    year = Annotated[
        int,
        Option(help="Year written (use negative int for BCE)", show_default=False),
    ]
    genre = Annotated[str, Option(help="Genre of the work", show_default=False)]
    is_read = Annotated[bool, Option(help="Whether the work has been read")]


class BookArguments:
    """Class to store argument definitions for book-related commands"""

    pages = Annotated[int, Option(help="Pages in the book", show_default=False)]
    format = Annotated[
        BookFormat,
        Option(
            case_sensitive=False, help="Format/medium of the book", show_default=False
        ),
    ]
    isbn = Annotated[
        str,
        Option(help="ISBN-13 (or ISBN-10 converted) of the book", show_default=False),
    ]
    add_book = Annotated[bool, Option(help="Associate work with book a in database")]


class SearchArguments:
    """Class to store argument definitions for search-related commands"""

    title = Annotated[
        Optional[List[str]],
        Option("--title", "-t", help="Title of the work"),
    ]
    author = Annotated[
        Optional[List[str]],
        Option("--author", "-a", help="Author of the work"),
    ]
    year = Annotated[
        Optional[List[int]],
        Option("--year", "-y", help="Year written"),
    ]
    year_from = Annotated[
        Optional[int],
        Option("--year-from", help="Start year for range search"),
    ]
    year_to = Annotated[
        Optional[int],
        Option("--year-to", help="End year for range search"),
    ]
    genre = Annotated[
        Optional[List[str]],
        Option("--genre", "-g", help="Genre of the work"),
    ]
    is_read = Annotated[
        Optional[bool],
        Option("--read/--unread", help="Filter by read status"),
    ]
    pages = Annotated[
        Optional[List[int]],
        Option("--pages", help="Number of pages"),
    ]
    pages_min = Annotated[
        Optional[int],
        Option("--pages-min", help="Minimum number of pages"),
    ]
    pages_max = Annotated[
        Optional[int],
        Option("--pages-max", help="Maximum number of pages"),
    ]
    format = Annotated[
        Optional[BookFormat],
        Option(
            "--format", "-f", case_sensitive=False, help="Format/medium of the book"
        ),
    ]
    isbn = Annotated[
        Optional[List[str]],
        Option("--isbn", "-i", help="ISBN-13 or ISBN-10 of the book"),
    ]
    limit = Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Maximum number of results to display",
            show_default=True,
        ),
    ]
