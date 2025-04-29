#############################################
# Tests mostly created by Claude 3.7 Sonnet #
#############################################

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import typer
from sqlmodel import Session, SQLModel, create_engine
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
from db import _get_session

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
    work = Work(title="sample work", author="test author", year=2020, genre="fiction", is_read=True)
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
        isbn="9780987654321"
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
            isbn="9781122334455"
        )
    
    assert work is not None
    assert work.title == "new work"
    assert work.author == "new author"
    
    books = session.query(Book).filter(Book.work_id == work.id).all()
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
            isbn=None
        )
    
    assert work is not None
    assert work.title == "work only"
    
    books = session.query(Book).filter(Book.work_id == work.id).all()
    assert len(books) == 0


def test_add_command_new_work(mock_session):
    """Test the add command for creating a new work and book."""
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=None), \
         patch.object(BookCommands, "_create_work_and_book") as mock_create:
        
        result = runner.invoke(
            app, 
            ["add", "new book", "new author", "--year", "2023", "--genre", "fantasy", 
             "--pages", "400", "--format", "print", "--isbn", "9781234567897"]
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
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=sample_work), \
         patch("typer.confirm", return_value=True), \
         patch.object(BookCommands, "_add_book_to_work") as mock_add_book:
        
        result = runner.invoke(
            app, 
            ["add", "sample work", "test author", "--pages", "350", 
             "--format", "ebook", "--isbn", "9780987654321"]
        )
        
        mock_add_book.assert_called_once()
        call_args = mock_add_book.call_args[1]
        assert call_args["work"] == sample_work
        assert call_args["pages"] == 350
        assert call_args["format"] == BookFormat.ebook


def test_add_command_existing_work_no_book(mock_session, sample_work):
    """Test the add command when work exists but no book is added."""
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=sample_work):
        
        result = runner.invoke(
            app, 
            ["add", "sample work", "test author"]
        )
        
        assert result.exit_code == 0


def test_add_book_command_work_not_found_abort(mock_session):
    """Test add_book when work not found and user aborts."""
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=None), \
         patch("typer.confirm", return_value=False):
        
        result = runner.invoke(
            app, 
            ["add-book", "unknown work", "unknown author", "--pages", "100"]
        )
        
        assert result.exit_code == 0


def test_add_work_command_new(mock_session):
    """Test the add_work command for a new work."""
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=None):
        
        result = runner.invoke(
            app, 
            ["add-work", "new work", "new author", "--year", "2021", "--genre", "history"]
        )
        
        assert result.exit_code == 0


def test_add_work_command_existing(mock_session, sample_work):
    """Test the add_work command when work already exists."""
    with patch("books.books.console.print"), \
         patch.object(BookCommands, "_find_work", return_value=sample_work):
        
        result = runner.invoke(
            app, 
            ["add-work", "sample work", "test author"]
        )
        
        assert result.exit_code == 1
