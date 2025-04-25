# Standard library imports
import os
from typing import Annotated, List, Optional

# Third-party imports
import typer
from rich.console import Console
from rich.table import Table


# Create Typer app
app = typer.Typer(help="Book collection manager")
console = Console()


class BookArguments:
    """Class to store argument definitions for book-related commands"""

    # Common arguments
    title = Annotated[str, typer.Argument(help="Title of the book", show_default=False)]
    author = Annotated[
        str, typer.Argument(help="Author of the book", show_default=False)
    ]
    year = Annotated[
        int,
        typer.Argument(
            help="Year written (use negative int for books BCE)", show_default=False
        ),
    ]
    genre = Annotated[str, typer.Argument(help="Genre of the book", show_default=False)]
    is_read = Annotated[
        bool, typer.Argument(help="Bool: whether the work has been read")
    ]

    # Book-specific arguments
    add_work = Annotated[
        bool,
        typer.Argument(help="Bool: create a 'work' entry associated with this book"),
    ]

    # Optional arguments for search/filter operations
    search_term = Annotated[str, typer.Argument(help="Term to search for")]
    limit = Annotated[int, typer.Option(help="Limit number of results")]


class BookCommands:
    """Class containing all book-related commands"""

    @staticmethod
    @app.command()
    def add_book(
        title: BookArguments.title,
        author: BookArguments.author,
        year: BookArguments.year,
        genre: BookArguments.genre,
        is_read: BookArguments.is_read = True,
        add_work: BookArguments.add_work = True,
    ):
        """Add a new book to the collection"""
        # Logic to add a book
        console.print(f"Adding book: {title} by {author} ({year})")
        console.print(f"Genre: {genre}, Read: {is_read}, Add work: {add_work}")

    @staticmethod
    @app.command()
    def search_books(
        search_term: BookArguments.search_term,
        limit: BookArguments.limit = 10,
    ):
        """Search for books in the collection"""
        # Logic to search books
        console.print(f"Searching for '{search_term}' (limit: {limit})")

    @staticmethod
    @app.command()
    def update_book(
        title: BookArguments.title,
        author: Optional[BookArguments.author] = None,
        genre: Optional[BookArguments.genre] = None,
        is_read: Optional[BookArguments.is_read] = None,
    ):
        """Update an existing book in the collection"""
        # Logic to update a book
        console.print(f"Updating book: {title}")
        if author:
            console.print(f"New author: {author}")
        if genre:
            console.print(f"New genre: {genre}")
        if is_read is not None:
            console.print(f"Read status: {is_read}")


class WorkArguments:
    """Class to store argument definitions for work-related commands"""

    # Work-specific arguments
    title = Annotated[str, typer.Argument(help="Title of the work", show_default=False)]
    author = Annotated[
        str, typer.Argument(help="Author of the work", show_default=False)
    ]
    year = Annotated[int, typer.Argument(help="Year created", show_default=False)]
    medium = Annotated[
        str, typer.Argument(help="Medium of the work", show_default=False)
    ]


class WorkCommands:
    """Class containing all work-related commands"""

    @staticmethod
    @app.command()
    def add_work(
        title: WorkArguments.title,
        author: WorkArguments.author,
        year: WorkArguments.year,
        medium: WorkArguments.medium,
    ):
        """Add a new work to the collection"""
        # Logic to add a work
        console.print(f"Adding work: {title} by {author} ({year})")
        console.print(f"Medium: {medium}")


# Main function to run the app
if __name__ == "__main__":
    app()
