import os
from enum import Enum
from typing import Annotated, List, Optional
from sqlite3 import IntegrityError


import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import select

from db import _get_session
from books.models import Book, Work, Review
from utils import validate_isbn, lowercase_args

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
        typer.Argument(help="Title of the work", show_default=False),
    ]
    author = Annotated[
        str,
        typer.Argument(help="Author of the work", show_default=False),
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
    @lowercase_args
    def add(
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
        """Add a new work (and book) to the collection"""
        with _get_session() as session:
            # Validate ISBN if provided
            if add_book and isbn:
                isbn = BookCommands._validate_isbn(isbn)
            
            # Check if work already exists
            work_exists = BookCommands._find_work(session,title, author) 
            if work_exists:
                console.print(f"{title} by {author} already exists in the database.")
                
                if add_book and typer.confirm("Add book to existing work?"):
                    book = Book(pages=pages,
                            format=format,
                            isbn=isbn,
                            work_id=work_exists.id)  # Use work_id directly
                    session.add(book)
                    try:
                        session.commit()
                        console.print(f"Added book to existing work '{work_exists.title}'")
                    except IntegrityError as e:
                        session.rollback()
                        console.print("Error: This book may already exist for this work")
                        console.print(f"Details: {str(e)}")
                else:
                    console.print("No changes made.")
            else:
                # Work doesn't exist, create it
                work = Work(title=title,
                        author=author,
                        year=year,
                        genre=genre,
                        is_read=is_read,
                        review=None)
                session.add(work)
                
                if add_book:
                    book = Book(pages=pages,
                            format=format,
                            isbn=isbn,
                            work=work)
                    session.add(book)
                
                try:
                    session.commit()
                    console.print(f"Added {title} by {author} to database")
                    
                    if add_book:
                        session.refresh(work)
                        session.refresh(book)
                        console.print(f"Also added book: {book}")
                except IntegrityError as e:
                    session.rollback()
                    console.print(f"Error adding record: {str(e)}")
                    console.print("This might be due to a race condition or another constraint violation.")

    @staticmethod
    @app.command()
    @lowercase_args
    def add_book(
        title: WorkArguments.title,
        author: WorkArguments.author,
        pages: BookArguments.pages = None,
        format: BookArguments.format = None,
        isbn: BookArguments.isbn = None,
    ):
        with _get_session() as session:
        # Get existing work to associate book with
            work = BookCommands._find_work(session,title, author)
            book = Book(pages=pages,
                        format=format,
                        isbn=validate_isbn(isbn),
                        work=work)
            if work:
                    session.add(book)
                    session.commit()
                    console.print(f"Added {title} by {author} book to database")
            else:
                if typer.confirm("Work not found. Do you want to add it now?"):
                    work = BookCommands.add_work(title, author)
                    book.work = work
                    session.add(book)
                    session.commit()
                    console.print(f"Added {title} by {author} book instance to database")
                    raise typer.Exit(code=0)
                
                console.print(f"No changes made.")

    @staticmethod
    @app.command()
    @lowercase_args
    def add_work(
            title: WorkArguments.title,
            author: WorkArguments.author,
            year: WorkArguments.year = None,
            genre: WorkArguments.genre = None,
            is_read: WorkArguments.is_read = True,
            ):
        """Add a new work to the collection"""
        with _get_session() as session:
            # Check if work already exists
            work_exists = BookCommands._find_work(session,title, author) 
            if work_exists:
                console.print(f"{title} by {author} already exists in the database.")
                console.print("No changes made.")
                raise typer.Exit(code=1)

            work = Work(title=title,
                        author=author,
                        year=year,
                        genre=genre,
                        is_read=is_read,
                        review=None)
            session.add(work)
            session.commit()
            console.print(f"Added {title} by {author} to database")
            
            return work

    @staticmethod
    @lowercase_args
    def _find_work(session,
                title: WorkArguments.title,
                author: WorkArguments.author):
        return session.exec(
                select(Work).where(
                    Work.title == title.lower(),
                    Work.author == author.lower()
                )
            ).first()
        
    @staticmethod
    def _validate_isbn(isbn):
        try:
            return validate_isbn(isbn)
        except ValueError:
            console.print(f"Invalid ISBN: {isbn} - must be valid ISBN-10 or ISBN-13")
            
            if typer.confirm("Continue with NULL ISBN?"):
                isbn = None
            else:
                console.print("Exiting...")
                raise typer.Abort()

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
