# Stanard imports
import os
from sqlite3 import IntegrityError

# Third-party imports
import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import select

# Folio imports
from db.db import SessionManager
from db.query_builder import QueryBuilder as Query
from books.args import SearchArgs, CreateArgs, UpdateArgs
from books.models import Book, Work, Review
from books.schemas import SearchCriteria, UpdateData
from utils import validate_isbn, lowercase_args


app = typer.Typer(help="Book collection manager", no_args_is_help=True)
console = Console()


class BookCommands:
    """Class containing all book-related commands"""

    @staticmethod
    @app.command()
    def add(
        title: CreateArgs.title,
        author: CreateArgs.author,
        year: CreateArgs.year = None,
        genre: CreateArgs.genre = None,
        pages: CreateArgs.pages = None,
        format: CreateArgs.format = None,
        isbn: CreateArgs.isbn = None,
        is_read: CreateArgs.is_read = True,
        add_book: CreateArgs.add_book = True,
    ):
        """Add a new work (and book) to the collection"""
        with SessionManager() as session:
            # Validate ISBN if provided
            if add_book and isbn:
                isbn = BookCommands._validate_isbn(isbn)

            # Check if work already exists
            existing_work = BookCommands._find_work(session, title, author)

            if existing_work:
                console.print(f"{title} by {author} already exists in the database.")

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
    def add_book(
        title: CreateArgs.title,
        author: CreateArgs.author,
        pages: CreateArgs.pages = None,
        format: CreateArgs.format = None,
        isbn: CreateArgs.isbn = None,
    ):
        """Add a book instance to an existing work, or create a new work if needed"""
        with SessionManager() as session:
            # Get existing work to associate book with
            if isbn:
                isbn = BookCommands._validate_isbn(isbn)
            work = BookCommands._find_work(session, title, author)

            if work:
                BookCommands._add_book_to_work(
                    session=session, work=work, pages=pages, format=format, isbn=isbn
                )
                console.print(f"Added {title} by {author} book to database")
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
    def add_work(
        title: CreateArgs.title,
        author: CreateArgs.author,
        year: CreateArgs.year = None,
        genre: CreateArgs.genre = None,
        is_read: CreateArgs.is_read = True,
    ):
        """Add a new work to the collection"""
        with SessionManager() as session:
            # Check if work already exists
            work_exists = BookCommands.search(
                session=session, title=title, author=author
            )
            if work_exists:
                console.print(f"{title} by {author} already exists in the database.")
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
            console.print(f"Added {title} by {author} to database")

            return work

    @staticmethod
    @lowercase_args
    @app.command()
    def search(
        title: SearchArgs.title = None,
        author: SearchArgs.author = None,
        year: SearchArgs.year = None,
        year_min: SearchArgs.year_min = None,
        year_max: SearchArgs.year_max = None,
        genre: SearchArgs.genre = None,
        is_read: SearchArgs.is_read = None,
        pages: SearchArgs.pages = None,
        pages_min: SearchArgs.pages_min = None,
        pages_max: SearchArgs.pages_max = None,
        format: SearchArgs.format = None,
        isbn: SearchArgs.isbn = None,
        work_id: SearchArgs.work_id = None,
        book_id: SearchArgs.book_id = None,
        limit: SearchArgs.limit = None,
        session=None,
    ):
        """Search for works and books with optional session parameter"""
        # Store whether this is a direct command call before entering context manager
        is_direct_call = session is None

        search_filters = SearchCriteria(
            title=title,
            author=author,
            year=year,
            year_min=year_min,
            year_max=year_max,
            genre=genre,
            is_read=is_read,
            pages=pages,
            pages_min=pages_min,
            pages_max=pages_max,
            format=format,
            isbn=isbn,
            work_id=work_id,
            book_id=book_id,
        )

        if search_filters.is_empty():
            print("No filters provided.")
            raise typer.Abort()

        with SessionManager(session) as session:
            query = (
                Query(session=session, model=Work)
                .join(Book)
                .text_filter(Work.title, search_filters.title)
                .text_filter(Work.author, search_filters.author)
                .range_filter(
                    Work.year,
                    min_value=search_filters.year_min,
                    max_value=search_filters.year_max,
                    exact_value=search_filters.year,
                )
                .text_filter(Work.genre, search_filters.genre)
                .boolean_filter(Work.is_read, search_filters.is_read)
                .range_filter(
                    Book.pages,
                    min_value=search_filters.pages_min,
                    max_value=search_filters.pages_max,
                    exact_value=search_filters.pages,
                )
                .text_filter(Book.format, search_filters.format)
                .exact_match(Book.isbn, value=search_filters.isbn)
                .exact_match(Work.id, search_filters.work_id)
                .exact_match(Book.id, search_filters.book_id)
            )

            results = query.run(limit=limit)

            # Only print results if this is a direct command call (no session passed)
            if is_direct_call:
                for result in results:
                    print(result, *result.books, sep="\n")

            return results

    @staticmethod
    @app.command()
    def update(
        # Search arguments
        title: SearchArgs.title = None,
        author: SearchArgs.author = None,
        year: SearchArgs.year = None,
        year_min: SearchArgs.year_min = None,
        year_max: SearchArgs.year_max = None,
        genre: SearchArgs.genre = None,
        is_read: SearchArgs.is_read = None,
        pages: SearchArgs.pages = None,
        pages_min: SearchArgs.pages_min = None,
        pages_max: SearchArgs.pages_max = None,
        format: SearchArgs.format = None,
        isbn: SearchArgs.isbn = None,
        work_id: SearchArgs.work_id = None,
        book_id: SearchArgs.book_id = None,
        # Update arguments
        set_title: UpdateArgs.set_title = None,
        set_author: UpdateArgs.set_author = None,
        set_year: UpdateArgs.set_year = None,
        set_genre: UpdateArgs.set_genre = None,
        set_is_read: UpdateArgs.set_is_read = None,
        set_pages: UpdateArgs.set_pages = None,
        set_format: UpdateArgs.set_format = None,
        set_isbn: UpdateArgs.set_isbn = None,
    ):
        search_filters = SearchCriteria(
            title=title,
            author=author,
            year=year,
            year_min=year_min,
            year_max=year_max,
            genre=genre,
            is_read=is_read,
            pages=pages,
            pages_min=pages_min,
            pages_max=pages_max,
            format=format,
            isbn=isbn,
            work_id=work_id,
            book_id=book_id,
        )

        update_values = UpdateData(
            title=set_title,
            author=set_author,
            year=set_year,
            genre=set_genre,
            is_read=set_is_read,
            pages=set_pages,
            format=set_format,
            isbn=set_isbn,
        ).exclude_none_fields()

        # Check if any filters were provided prior to making a db query
        if search_filters.is_empty():
            print("No filters provided. Search aborted")
            raise typer.Abort()

        if update_values.is_empty():
            print("No update values provided. Update aborted.")
            raise typer.Abort()

        work_updates, book_updates = update_values.split_work_and_book_args()

        with SessionManager() as session:
            results = BookCommands.search(session=session, **search_filters.to_dict())

            match len(results):
                case 0:
                    print(f"No results found with \n{search_filters}")
                    return []
                case 1:
                    result = results[0]
                    # TODO: Add logic to short-circuit update if update values == existing values
                    books_str = "\n".join(
                        f"{i+1}. {book}" for i, book in enumerate(result.books)
                    )
                    books_count = len(result.books)
                    if books_count == 0:
                        book_summary = "No associated books."
                    elif books_count == 1:
                        book_summary = books_str
                    else:
                        book_summary = f"{books_str}\nYou will be able to select which books to update."

                    if typer.confirm(f"Found {result}\n{book_summary}\nContinue?"):
                        if work_updates:
                            for field, value in work_updates:
                                setattr(result, field, value)
                                session.add(result)

                        if book_updates and len(result.books) > 1:
                            book_indices = typer.prompt(
                                f"Which books to update? (1-{len(result.books)}, comma-separated, 'all', or 'skip')"
                            )

                            if book_indices.lower() == "all":
                                selected_books = result.books
                            elif book_indices.lower() == "skip":
                                selected_books = None
                            else:
                                indices = [
                                    int(x.strip()) - 1 for x in book_indices.split(",")
                                ]
                                selected_books = [
                                    result.books[i]
                                    for i in indices
                                    if 0 <= i < len(result.books)
                                ]

                            if selected_books:
                                for book in selected_books:
                                    for field, value in book_updates:
                                        setattr(book, field, value)
                                        session.add(book)
                        elif book_updates:
                            # Only one book, update directly
                            for field, value in book_updates:
                                setattr(result.books[0], field, value)
                                session.add(result.books[0])
                        session.commit()
                        session.refresh(result)
                        # TODO: Add color to fields that have changed
                        books_str = "\n".join(
                            f"{i+1}. {book}" for i, book in enumerate(result.books)
                        )
                        print(f"Update successful. New entry:\n{result}\n{books_str}")
                        return result
                case _:
                    # TODO
                    for result in results:
                        print(result)
                    if typer.confirm(
                        f"Found multiple results. Continue with bulk update?"
                    ):
                        print("Multiple")

    @staticmethod
    @app.command()
    def delete():
        """TODO: Not implemented"""
        pass

    @staticmethod
    @lowercase_args
    def _find_work(session, title: SearchArgs.title, author: SearchArgs.author):
        """
        NOTE: DEPRECATED, use BookCommands.search instead.
        Find a work by title and author
        """
        return session.exec(
            select(Work).where(
                Work.title == title.lower(), Work.author == author.lower()
            )
        ).first()

    @staticmethod
    def _create_work_and_book(
        session,
        title: CreateArgs.title,
        author: CreateArgs.author,
        year: CreateArgs.year = None,
        genre: CreateArgs.genre = None,
        is_read: CreateArgs.is_read = True,
        add_book: CreateArgs.add_book = True,
        pages: CreateArgs.pages = None,
        format: CreateArgs.format = None,
        isbn: CreateArgs.isbn = None,
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

        console.print(f"Added {title} by {author} to collection (read: {is_read})")
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
        pages: CreateArgs.pages,
        format: CreateArgs.format,
        isbn: CreateArgs.isbn,
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
