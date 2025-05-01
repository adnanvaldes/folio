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
