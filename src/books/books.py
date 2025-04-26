import os
from enum import Enum
from typing import Annotated, List, Optional


import typer
from rich.console import Console
from rich.table import Table


# Create Typer app
app = typer.Typer(help="Book collection manager")
console = Console()


class BookFormat(str, Enum):
    print = "print"
    ebook = "ebook"
    audio = "audiobook"


class WorkArguments:
    """Class to store argument definitions for work-related commands"""

    title = Annotated[
        str,
        typer.Argument(help="Title of the work"),
    ]
    author = Annotated[
        str,
        typer.Argument(help="Author of the work"),
    ]
    year = Annotated[
        int,
        typer.Option(
            help="Year written (use negative int for BCE)", show_default=False
        ),
    ]
    genre = Annotated[str, typer.Option(help="Genre of the work", show_default=False)]
    is_read = Annotated[bool, typer.Option(help="Whether the work has been read")]


class BookArguments:
    """Class to store argument definitions for book-related commands"""

    pages = Annotated[int, typer.Option(help="Pages in the book", show_default=False)]
    format = Annotated[
        BookFormat,
        typer.Option(
            case_sensitive=False, help="Format/medium of the book", show_default=False
        ),
    ]
    isbn = Annotated[
        str,
        typer.Option(
            help="ISBN-13 (or ISBN-10 converted) of the book", show_default=False
        ),
    ]
    add_book = Annotated[
        bool, typer.Option(help="Associate work with book a in database")
    ]


class BookCommands:
    """Class containing all book-related commands"""

    @staticmethod
    @app.command()
    def add_book(
        title: WorkArguments.title,
        author: WorkArguments.author,
        year: WorkArguments.year = None,
        genre: WorkArguments.genre = None,
        pages: BookArguments.pages = None,
        format: BookArguments.format = None,
        isbn: BookArguments.isbn = None,
        is_read: WorkArguments.is_read = True,
        add_book: BookArguments.add_book = True,
    ):
        """Add a new work to the collection"""
        # Logic to add a book

        console.print(f"Adding book: {title} by {author} ({year})")
        console.print(f"Genre: {genre}, Read: {is_read}, Add book: {add_book}")

    @staticmethod
    @app.command()
    def add_book_interactive():
        pass

    # @staticmethod
    # @app.command()
    # def search_books(
    #     search_term: BookArguments.search_term,
    #     limit: BookArguments.limit = 10,
    # ):
    #     """Search for books in the collection"""
    #     # Logic to search books
    #     console.print(f"Searching for '{search_term}' (limit: {limit})")

    # @staticmethod
    # @app.command()
    # def update_book(
    #     title: BookArguments.title,
    #     author: Optional[BookArguments.author] = None,
    #     genre: Optional[BookArguments.genre] = None,
    #     is_read: Optional[BookArguments.is_read] = None,
    # ):
    #     """Update an existing book in the collection"""
    #     # Logic to update a book
    #     console.print(f"Updating book: {title}")
    #     if author:
    #         console.print(f"New author: {author}")
    #     if genre:
    #         console.print(f"New genre: {genre}")
    #     if is_read is not None:
    #         console.print(f"Read status: {is_read}")


# class WorkCommands:
#     """Class containing all work-related commands"""

#     @staticmethod
#     @app.command()
#     def add_work(
#         title: WorkArguments.title,
#         author: WorkArguments.author,
#         year: WorkArguments.year,
#         medium: WorkArguments.medium,
#     ):
#         """Add a new work to the collection"""
#         # Logic to add a work
#         console.print(f"Adding work: {title} by {author} ({year})")
#         console.print(f"Medium: {medium}")


# # Main function to run the app
# if __name__ == "__main__":
#     app()
