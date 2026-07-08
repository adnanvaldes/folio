import pytest
import sqlite3
from folio.models.book import Book, FormatType
from folio.models.work import Work
from folio.repositories.sql.sqlite_book_repository import SQLiteBookRepository
from folio.repositories.sql.sqlite_work_repository import SQLiteWorkRepository


A_WORK = Work(
    author="Brandon Sanderson",
    title="The Way of Kings",
    year=2010,
    genre="Fantasy",
    is_read=True,
)


@pytest.fixture
def repo(fake_db):
    conn = sqlite3.connect(fake_db)
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN")
    work_repo = SQLiteWorkRepository(conn)
    work_repo.add(A_WORK)
    return SQLiteBookRepository(conn)


def make_book(**overrides) -> Book:
    defaults = dict(
        work=A_WORK,
        format_type=FormatType.PRINT,
        isbn="9780765326355",
        pages=1007,
    )
    return Book(**{**defaults, **overrides})


class TestSQLiteBookRepositoryAdd:

    def test_add_and_list(self, repo):
        book = make_book()
        repo.add(book)
        assert book in repo.list()

    def test_add_duplicate_raises(self, repo):
        book = make_book()
        repo.add(book)
        with pytest.raises(ValueError, match="already exists"):
            repo.add(book)

    def test_list_returns_ordered(self, repo):
        b1 = make_book(
            work=Work(
                author="Z Author",
                title="Last",
                year=2020,
                genre="Fiction",
                is_read=True,
            ),
            isbn="9780000000033",
        )
        b2 = make_book(
            work=Work(
                author="A Author",
                title="First",
                year=2020,
                genre="Fiction",
                is_read=True,
            ),
            isbn="9780000000040",
        )
        work_repo = SQLiteWorkRepository(repo.conn)
        work_repo.add(b1.work)
        work_repo.add(b2.work)
        repo.add(b2)
        repo.add(b1)
        result = repo.list()
        assert result == [b2, b1]

    def test_add_audio_book(self, repo):
        work = Work(
            author="Brandon Sanderson",
            title="Words of Radiance",
            year=2014,
            genre="Fantasy",
            is_read=True,
        )
        work_repo = SQLiteWorkRepository(repo.conn)
        work_repo.add(work)
        book = make_book(
            work=work,
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
        )
        repo.add(book)
        assert book in repo.list()


class TestSQLiteBookRepositoryNullHandling:

    def test_isbn_none_round_trips_as_none(self, repo):
        book = make_book(isbn=None)
        repo.add(book)
        retrieved = repo.list()[0]
        assert retrieved.isbn is None

    def test_narrator_none_round_trips_as_none(self, repo):
        book = make_book()
        repo.add(book)
        retrieved = repo.list()[0]
        assert retrieved.narrator is None

    def test_narrator_value_round_trips_correctly(self, repo):
        work = Work(
            author="Brandon Sanderson",
            title="Words of Radiance",
            year=2014,
            genre="Fantasy",
            is_read=True,
        )
        work_repo = SQLiteWorkRepository(repo.conn)
        work_repo.add(work)
        book = make_book(
            work=work,
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
            narrator="Michael Kramer",
        )
        repo.add(book)
        retrieved = repo.list()[0]
        assert retrieved.narrator == "Michael Kramer"


class TestSQLiteBookRepositoryRemove:

    def test_remove_existing_book(self, repo):
        book = make_book()
        repo.add(book)
        repo.remove(book)
        assert book not in repo.list()

    def test_remove_nonexistent_raises(self, repo):
        book = make_book()
        with pytest.raises(ValueError, match="not found"):
            repo.remove(book)

    def test_remove_isbn_none_uses_is_null(self, repo):
        book = make_book(isbn=None)
        repo.add(book)
        repo.remove(book)
        assert repo.list() == []


class TestSQLiteBookRepositoryReplace:

    def test_replace_updates_book(self, repo):
        original = make_book()
        repo.add(original)

        corrected = make_book(isbn="9780000000026")
        repo.replace(original, corrected)

        result = repo.list()
        assert len(result) == 1
        assert result[0].isbn == "9780000000026"

    def test_replace_nonexistent_raises(self, repo):
        original = make_book()
        corrected = make_book(isbn="9780000000026")
        with pytest.raises(ValueError, match="not found"):
            repo.replace(original, corrected)

    def test_replace_isbn_none_uses_is_null(self, repo):
        book = make_book(isbn=None)
        repo.add(book)

        updated = make_book(isbn="9780765326355")
        repo.replace(book, updated)

        result = repo.list()
        assert result[0].isbn == "9780765326355"


class TestSQLiteBookRepositoryFind:

    def test_find_by_author(self, repo):
        b1 = make_book()
        other_work = Work(
            author="Robert Jordan",
            title="The Eye of the World",
            year=1990,
            genre="Fantasy",
            is_read=True,
        )
        b2 = make_book(work=other_work, isbn="9780000000026")
        work_repo = SQLiteWorkRepository(repo.conn)
        work_repo.add(other_work)
        repo.add(b1)
        repo.add(b2)

        results = repo.find(author="Brandon Sanderson")
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_isbn_none_uses_is_null(self, repo):
        b1 = make_book(isbn=None)
        b2 = make_book(isbn="9780000000026")
        repo.add(b1)
        repo.add(b2)

        results = repo.find(isbn=None)
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_format_type(self, repo):
        b1 = make_book()
        b2 = make_book(format_type=FormatType.EBOOK, isbn="9780000000026")
        repo.add(b1)
        repo.add(b2)

        results = repo.find(format_type=FormatType.PRINT)
        assert len(results) == 1
        assert results[0] == b1

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            repo.find(nonexistent="value")

    def test_find_empty_returns_all(self, repo):
        b1 = make_book()
        b2 = make_book(isbn="9780000000026")
        repo.add(b1)
        repo.add(b2)

        results = repo.find()
        assert len(results) == 2
