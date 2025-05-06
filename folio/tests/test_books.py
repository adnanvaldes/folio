#############################################
# Tests mostly created by Claude 3.7 Sonnet #
#############################################

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import typer
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

import sys
import os
from pathlib import Path

# To make imports work
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from books.models import Book, Work, Review
from books.books import BookCommands, BookFormat, app
from db.db import _get_session

# Test runner for CLI commands
runner = CliRunner()


# Create in-memory database for testing
@pytest.fixture
def session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def mock_session(session):
    """Patch the _get_session function to return our test session."""
    with patch("books.books._get_session") as mock:
        mock.return_value.__enter__.return_value = session
        mock.return_value.__exit__.return_value = None
        yield mock


# Test data fixtures
@pytest.fixture
def sample_work(session):
    """Create a sample work in the database."""
    work = Work(
        title="sample work",
        author="test author",
        year=2020,
        genre="fiction",
        is_read=True,
    )
    session.add(work)
    session.commit()
    return work


@pytest.fixture
def sample_book(session, sample_work):
    """Create a sample book associated with the sample work."""
    book = Book(pages=200, format="print", isbn="9781234567897", work_id=sample_work.id)
    session.add(book)
    session.commit()
    return book


def test_find_work(session, sample_work):
    """Test the _find_work method."""
    found_work = BookCommands._find_work(session, "sample work", "test author")
    assert found_work is not None
    assert found_work.id == sample_work.id

    not_found = BookCommands._find_work(session, "nonexistent", "nobody")
    assert not_found is None


def test_validate_isbn():
    """Test the _validate_isbn method."""
    with patch("typer.confirm", return_value=True):
        assert BookCommands._validate_isbn("invalid-isbn") is None


def test_validate_isbn_abort():
    """Test _validate_isbn when user chooses to abort."""
    with patch("typer.confirm", return_value=False), pytest.raises(typer.Abort):
        BookCommands._validate_isbn("invalid-isbn")


def test_add_book_to_work(session, sample_work):
    """Test adding a book to an existing work."""
    book = BookCommands._add_book_to_work(
        session=session,
        work=sample_work,
        pages=300,
        format=BookFormat.ebook,
        isbn="9780987654321",
    )

    assert book is not None
    assert book.work_id == sample_work.id
    assert book.pages == 300
    assert book.format == "ebook"


def test_create_work_and_book(session):
    """Test creating a new work with an associated book."""
    with patch("books.books.console.print"):
        work = BookCommands._create_work_and_book(
            session=session,
            title="new work",
            author="new author",
            year=2022,
            genre="mystery",
            is_read=True,
            add_book=True,
            pages=250,
            format=BookFormat.print,
            isbn="9781122334455",
        )

    assert work is not None
    assert work.title == "new work"
    assert work.author == "new author"

    books = session.exec(select(Book).where(Book.work_id == work.id)).all()
    assert len(books) == 1
    assert books[0].pages == 250
    assert books[0].format == "print"


def test_create_work_without_book(session):
    """Test creating a work without adding a book."""
    with patch("books.books.console.print"):
        work = BookCommands._create_work_and_book(
            session=session,
            title="work only",
            author="some author",
            year=2021,
            genre="science",
            is_read=False,
            add_book=True,
            pages=None,
            format=None,
            isbn=None,
        )

    assert work is not None
    assert work.title == "work only"

    books = session.exec(select(Book).where(Book.work_id == work.id)).all()
    assert len(books) == 0


def test_add_command_new_work(mock_session):
    """Test the add command for creating a new work and book."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=None),
        patch.object(BookCommands, "_create_work_and_book") as mock_create,
    ):

        result = runner.invoke(
            app,
            [
                "add",
                "new book",
                "new author",
                "--year",
                "2023",
                "--genre",
                "fantasy",
                "--pages",
                "400",
                "--format",
                "print",
                "--isbn",
                "9781234567897",
            ],
        )

        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        assert call_args["title"] == "new book"
        assert call_args["author"] == "new author"
        assert call_args["year"] == 2023
        assert call_args["genre"] == "fantasy"
        assert call_args["pages"] == 400
        assert call_args["format"] == BookFormat.print
        assert call_args["isbn"] == "9781234567897"


def test_add_command_existing_work(mock_session, sample_work):
    """Test the add command when the work already exists."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=sample_work),
        patch("typer.confirm", return_value=True),
        patch.object(BookCommands, "_add_book_to_work") as mock_add_book,
    ):

        result = runner.invoke(
            app,
            [
                "add",
                "sample work",
                "test author",
                "--pages",
                "350",
                "--format",
                "ebook",
                "--isbn",
                "9780987654321",
            ],
        )

        mock_add_book.assert_called_once()
        call_args = mock_add_book.call_args[1]
        assert call_args["work"] == sample_work
        assert call_args["pages"] == 350
        assert call_args["format"] == BookFormat.ebook


def test_add_command_existing_work_no_book(mock_session, sample_work):
    """Test the add command when work exists but no book is added."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=sample_work),
    ):

        result = runner.invoke(app, ["add", "sample work", "test author"])

        assert result.exit_code == 0


def test_add_book_command_work_not_found_abort(mock_session):
    """Test add_book when work not found and user aborts."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=None),
        patch("typer.confirm", return_value=False),
    ):

        result = runner.invoke(
            app, ["add-book", "unknown work", "unknown author", "--pages", "100"]
        )

        assert result.exit_code == 0


def test_add_work_command_new(mock_session):
    """Test the add_work command for a new work."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=None),
    ):

        result = runner.invoke(
            app,
            [
                "add-work",
                "new work",
                "new author",
                "--year",
                "2021",
                "--genre",
                "history",
            ],
        )

        assert result.exit_code == 0


def test_add_work_command_existing(mock_session, sample_work):
    """Test the add_work command when work already exists."""
    with (
        patch("books.books.console.print"),
        patch.object(BookCommands, "_find_work", return_value=sample_work),
    ):

        result = runner.invoke(app, ["add-work", "sample work", "test author"])

        assert result.exit_code == 1


# Tests for search functionality


@pytest.fixture
def search_data(session):
    """Create various works and books for search testing."""
    # Work 1: Fiction book with multiple formats
    work1 = Work(
        title="the hobbit",
        author="j.r.r. tolkien",
        year=1937,
        genre="fantasy",
        is_read=True,
    )
    session.add(work1)
    session.commit()

    # Add two formats for work1
    book1a = Book(pages=300, format="print", isbn="9780261102217", work_id=work1.id)
    book1b = Book(pages=310, format="ebook", isbn="9780007322602", work_id=work1.id)
    session.add(book1a)
    session.add(book1b)

    # Work 2: Newer sci-fi book
    work2 = Work(
        title="project hail mary",
        author="andy weir",
        year=2021,
        genre="science fiction",
        is_read=False,
    )
    session.add(work2)
    session.commit()

    book2 = Book(pages=496, format="hardcover", isbn="9780593135204", work_id=work2.id)
    session.add(book2)

    # Work 3: Older non-fiction book, no physical copy
    work3 = Work(
        title="a brief history of time",
        author="stephen hawking",
        year=1988,
        genre="science",
        is_read=True,
    )
    session.add(work3)
    session.commit()

    book3 = Book(pages=256, format="audiobook", work_id=work3.id)
    session.add(book3)

    # Work 4: Similar author to work3
    work4 = Work(
        title="the theory of everything",
        author="stephen hawking",
        year=2002,
        genre="science",
        is_read=False,
    )
    session.add(work4)
    session.commit()

    book4 = Book(pages=176, format="print", isbn="9780521816267", work_id=work4.id)
    session.add(book4)

    # Work 5: Long novel
    work5 = Work(
        title="war and peace",
        author="leo tolstoy",
        year=1869,
        genre="historical fiction",
        is_read=False,
    )
    session.add(work5)
    session.commit()

    book5 = Book(pages=1225, format="print", isbn="9781400079988", work_id=work5.id)
    session.add(book5)

    session.commit()
    return [work1, work2, work3, work4, work5]


def test_search_by_title(mock_session, search_data):
    """Test searching by title."""
    with patch("books.books.console.print"):
        # Exact title match
        result = BookCommands.search(title="the hobbit")
        assert len(result) == 1
        assert result[0].title == "the hobbit"
        assert result[0].author == "j.r.r. tolkien"

        # Partial title match
        result = BookCommands.search(title="hobbit")
        assert len(result) == 1
        assert result[0].title == "the hobbit"

        # Case insensitive match
        result = BookCommands.search(title="HoBBiT")
        assert len(result) == 1
        assert result[0].title == "the hobbit"


def test_search_by_author(mock_session, search_data):
    """Test searching by author."""
    with patch("books.books.console.print"):
        # Exact author match
        result = BookCommands.search(author="stephen hawking")
        assert len(result) == 2
        assert all(work.author == "stephen hawking" for work in result)

        # Partial author match
        result = BookCommands.search(author="hawking")
        assert len(result) == 2
        assert all("hawking" in work.author for work in result)


def test_search_by_year_exact(mock_session, search_data):
    """Test searching by exact year."""
    with patch("books.books.console.print"):
        result = BookCommands.search(year=[1937])
        assert len(result) == 1
        assert result[0].title == "the hobbit"
        assert result[0].year == 1937


def test_search_by_year_exact_multiple(mock_session, search_data):
    """Test searching by exact year."""
    with patch("books.books.console.print"):
        result = BookCommands.search(year=[1937, 1988])
        assert len(result) == 2


def test_search_by_year_range(mock_session, search_data):
    """Test searching by year range."""
    with patch("books.books.console.print"):
        # Min year only
        result = BookCommands.search(year_min=2000)
        assert len(result) == 2
        assert all(work.year >= 2000 for work in result)

        # Max year only
        result = BookCommands.search(year_max=1950)
        assert len(result) == 2
        assert all(work.year <= 1950 for work in result)

        # Both min and max
        result = BookCommands.search(year_min=1980, year_max=2010)
        assert len(result) == 2
        assert all(1980 <= work.year <= 2010 for work in result)


def test_search_by_genre(mock_session, search_data):
    """Test searching by genre."""
    with patch("books.books.console.print"):
        # Exact genre match
        result = BookCommands.search(genre="fantasy")
        assert len(result) == 1
        assert result[0].genre == "fantasy"
        assert result[0].title == "the hobbit"

        # Partial genre match
        result = BookCommands.search(genre="science")
        assert len(result) == 3
        assert all("science" in work.genre for work in result)


def test_search_by_read_status(mock_session, search_data):
    """Test searching by read status."""
    with patch("books.books.console.print"):
        # Read books
        result = BookCommands.search(is_read=True)
        assert len(result) == 2
        assert all(work.is_read for work in result)

        # Unread books
        result = BookCommands.search(is_read=False)
        assert len(result) == 3
        assert all(not work.is_read for work in result)


def test_search_by_pages_exact(mock_session, search_data):
    """Test searching by exact page count."""
    with patch("books.books.console.print"):
        result = BookCommands.search(pages=[496])
        assert len(result) == 1
        assert result[0].title == "project hail mary"

        # Verify that the book has the expected page count
        books = mock_session.return_value.__enter__.return_value.exec(
            select(Book).where(Book.work_id == result[0].id)
        ).all()
        assert any(book.pages == 496 for book in books)


def test_search_by_pages_range(mock_session, search_data):
    """Test searching by page range."""
    with patch("books.books.console.print"):
        # Min pages only
        result = BookCommands.search(pages_min=500)
        assert len(result) == 1
        assert result[0].title == "war and peace"

        # Max pages only
        result = BookCommands.search(pages_max=200)
        assert len(result) == 1
        assert result[0].title == "the theory of everything"

        # Both min and max
        result = BookCommands.search(pages_min=250, pages_max=500)
        assert len(result) == 3
        # Verify all works have at least one book in the page range
        for work in result:
            books = mock_session.return_value.__enter__.return_value.exec(
                select(Book).where(Book.work_id == work.id)
            ).all()
            assert any(250 <= book.pages <= 500 for book in books)


def test_search_by_format(mock_session, search_data):
    """Test searching by book format."""
    with patch("books.books.console.print"):
        result = BookCommands.search(format="ebook")
        assert len(result) == 1
        assert result[0].title == "the hobbit"

        # Verify the work has a book with the ebook format
        books = mock_session.return_value.__enter__.return_value.exec(
            select(Book).where(Book.work_id == result[0].id)
        ).all()
        assert any(book.format == "ebook" for book in books)


def test_search_by_isbn(mock_session, search_data):
    """Test searching by ISBN."""
    with patch("books.books.console.print"):
        result = BookCommands.search(isbn="9780261102217")
        assert len(result) == 1
        assert result[0].title == "the hobbit"

        # Verify the work has a book with the ISBN
        books = mock_session.return_value.__enter__.return_value.exec(
            select(Book).where(Book.work_id == result[0].id)
        ).all()
        assert any(book.isbn == "9780261102217" for book in books)


def test_search_with_limit(mock_session, search_data):
    """Test search with result limit."""
    with patch("books.books.console.print"):
        # Without limit - should return 2 results
        result_no_limit = BookCommands.search(genre="science")
        assert len(result_no_limit) == 3

        # With limit - should return only 1 result
        result_limit = BookCommands.search(genre="science", limit=1)
        assert len(result_limit) == 1
        assert "science" in result_limit[0].genre


def test_search_combined_filters(mock_session, search_data):
    """Test search with multiple filters combined."""
    with patch("books.books.console.print"):
        # Author and read status
        result = BookCommands.search(author="hawking", is_read=True)
        assert len(result) == 1
        assert result[0].author == "stephen hawking"
        assert result[0].is_read is True
        assert result[0].title == "a brief history of time"

        # Year range and genre
        result = BookCommands.search(year_min=1980, year_max=2010, genre="science")
        assert len(result) == 2
        assert all(1980 <= work.year <= 2010 for work in result)
        assert all(work.genre == "science" for work in result)

        # Complex combination
        result = BookCommands.search(
            pages_min=200, year_max=2000, is_read=True, format="print"
        )
        assert len(result) == 1
        assert result[0].title == "the hobbit"
        assert result[0].year <= 2000
        assert result[0].is_read is True

        # Verify the work has a book with the print format and at least 200 pages
        books = mock_session.return_value.__enter__.return_value.exec(
            select(Book).where(Book.work_id == result[0].id)
        ).all()
        assert any(book.format == "print" and book.pages >= 200 for book in books)


def test_search_empty_results(mock_session, search_data):
    """Test search that returns no results."""
    with patch("books.books.console.print"):
        result = BookCommands.search(title="nonexistent book")
        assert len(result) == 0


def test_search_actual_results(mock_session, search_data):
    """Test that search returns the expected number of results."""
    with patch("books.books.console.print") as mock_print:
        # Search for all Hawking books
        results = BookCommands.search(author="hawking")
        assert len(results) == 2
        assert all("hawking" in work.author for work in results)

        # Search for read books
        results = BookCommands.search(is_read=True)
        assert len(results) == 2
        assert all(work.is_read for work in results)

        # Search for books with more than 1000 pages
        results = BookCommands.search(pages_min=1000)
        assert len(results) == 1
        assert results[0].title == "war and peace"

        # Verify the book has more than 1000 pages
        books = mock_session.return_value.__enter__.return_value.exec(
            select(Book).where(Book.work_id == results[0].id)
        ).all()
        assert any(book.pages >= 1000 for book in books)
