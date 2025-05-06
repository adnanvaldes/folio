# Stanard imports
import os
from sqlite3 import IntegrityError

# Third-party imports
import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import select

# Folio imports
from db.db import _get_session
from db.query_builder import QueryBuilder as query
from books.args import BookFormat, WorkArguments, BookArguments, SearchArguments
from books.models import Book, Work, Review
from utils import validate_isbn, lowercase_args


app = typer.Typer(help="Book collection manager", no_args_is_help=True)
console = Console()


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
            existing_work = BookCommands._find_work(session, title, author)

            if existing_work:
                console.print(
                    f"{title.capitalize()} by {author.title()} already exists in the database."
                )

                if add_book and any([pages, format, isbn]):
                    if typer.confirm("Add book to existing work?"):
                        BookCommands._add_book_to_work(
                            session=session,
                            work=existing_work,
                            pages=pages,
                            format=format,
                            isbn=isbn,
                        )
                else:
                    console.print("No changes made.")
            else:
                # Create new work and optoinally new book
                BookCommands._create_work_and_book(
                    session=session,
                    title=title,
                    author=author,
                    year=year,
                    genre=genre,
                    is_read=is_read,
                    add_book=add_book,
                    pages=pages,
                    format=format,
                    isbn=isbn,
                )

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
        """Add a book instance to an existing work, or create a new work if needed"""
        with _get_session() as session:
            # Get existing work to associate book with
            if isbn:
                isbn = BookCommands._validate_isbn(isbn)
            work = BookCommands._find_work(session, title, author)

            if work:
                BookCommands._add_book_to_work(
                    session=session, work=work, pages=pages, format=format, isbn=isbn
                )
                console.print(
                    f"Added {title.capitalize()} by {author.title()} book to database"
                )
            else:
                if typer.confirm("Work not found. Do you want to add it now?"):
                    BookCommands._create_work_and_book(
                        session=session,
                        title=title,
                        author=author,
                        pages=pages,
                        format=format,
                        isbn=isbn,
                    )
                else:
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
            work_exists = BookCommands._find_work(session, title, author)
            if work_exists:
                console.print(
                    f"{title.capitalize()} by {author.title()} already exists in the database."
                )
                console.print("No changes made.")
                raise typer.Exit(code=1)

            work = Work(
                title=title,
                author=author,
                year=year,
                genre=genre,
                is_read=is_read,
                review=None,
            )
            session.add(work)
            session.commit()
            console.print(f"Added {title.capitalize()} by {author.title()} to database")

            return work

    @staticmethod
    @lowercase_args
    @app.command()
    def search(
        title: SearchArguments.title = None,
        author: SearchArguments.author = None,
        year: SearchArguments.year = None,
        year_min: SearchArguments.year_from = None,
        year_max: SearchArguments.year_to = None,
        genre: SearchArguments.genre = None,
        is_read: SearchArguments.is_read = None,
        pages: SearchArguments.pages = None,
        pages_min: SearchArguments.pages_min = None,
        pages_max: SearchArguments.pages_max = None,
        format: SearchArguments.format = None,
        isbn: SearchArguments.isbn = None,
        limit: SearchArguments.limit = None,
    ):

        from db.query_builder import QueryBuilder as Query

        with _get_session() as session:
            query = (
                Query(session=session, model=Work)
                .join(Book)
                .text_filter(Work.title, title)
                .text_filter(Work.author, author)
                .range_filter(
                    Work.year,
                    min_value=year_min,
                    max_value=year_max,
                    exact_value=year,
                )
                .text_filter(Work.genre, genre)
                .boolean_filter(Work.is_read, is_read)
                .range_filter(
                    Book.pages,
                    min_value=pages_min,
                    max_value=pages_max,
                    exact_value=pages,
                )
                .text_filter(Book.format, format)
                .exact_match(Book.isbn, value=isbn)
            )

            return query.run(limit=limit)

    @staticmethod
    @app.command()
    def update():
        """TODO: Not implemented"""
        pass

    @staticmethod
    @app.command()
    def delete():
        """TODO: Not implemented"""
        pass

    @staticmethod
    @lowercase_args
    def _find_work(session, title: WorkArguments.title, author: WorkArguments.author):
        """Find a work by title and author"""
        return session.exec(
            select(Work).where(
                Work.title == title.lower(), Work.author == author.lower()
            )
        ).first()

    @staticmethod
    def _create_work_and_book(
        session,
        title: WorkArguments.title,
        author: WorkArguments.author,
        year: WorkArguments.year = None,
        genre: WorkArguments.genre = None,
        is_read: WorkArguments.is_read = True,
        add_book: BookArguments.add_book = True,
        pages: BookArguments.pages = None,
        format: BookArguments.format = None,
        isbn: BookArguments.isbn = None,
    ):
        """Create a new work, optionally add a book"""
        work = Work(title=title, author=author, year=year, genre=genre, is_read=is_read)
        session.add(work)
        session.flush()  # To get work.id

        # Add book if add_book and there is information available
        book = None
        if add_book:
            book = BookCommands._add_book_to_work(
                session=session, work=work, pages=pages, format=format, isbn=isbn
            )

        session.commit()

        console.print(
            f"Added {title.capitalize()} by {author.title()} to collection (read: {is_read})"
        )
        # Only print additional information if add_book was requested but not completed
        if add_book and not book:
            reason = (
                "due to errors"
                if any([pages, format, isbn])
                else "no information provided"
            )
            console.print(f"Book was not added ({reason})")

        return work

    @staticmethod
    def _add_book_to_work(
        session,
        work,
        pages: BookArguments.pages,
        format: BookArguments.format,
        isbn: BookArguments.isbn,
    ):
        """Add a new  book to an existing work"""
        if any([pages, format, isbn]):
            book = Book(pages=pages, format=format, isbn=isbn, work_id=work.id)
            session.add(book)
            try:
                session.commit()
                console.print(f"Added book to existing work '{work.title}'")
                return book
            except IntegrityError as e:
                session.rollback()
                console.print("Error: This book may already exist for this work")
                console.print(f"Details: {str(e)}")
                return None
        console.print("No data entered for book. No changes made.")
        return None

    @staticmethod
    def _validate_isbn(isbn):
        """Validate ISBN and handle errors"""
        try:
            return validate_isbn(isbn)
        except ValueError:
            console.print(f"Invalid ISBN: {isbn} - must be valid ISBN-10 or ISBN-13")

            if typer.confirm("Continue with NULL ISBN?"):
                isbn = None
            else:
                console.print("Exiting...")
                raise typer.Abort()
