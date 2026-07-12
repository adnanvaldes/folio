import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Book, FormatType, Work


@pytest.fixture
def work_repo(pg_conn, _pg_drop_tables):
    from folio.repositories import PgWorkRepository
    return PgWorkRepository(pg_conn)


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    from folio.repositories import PgBookRepository, PgWorkRepository
    work_repo = PgWorkRepository(pg_conn)
    w = Work(
        author="George Orwell", title="1984", year=1949, genre="Dystopian", is_read=True
    )
    work_repo.add(w)
    return PgBookRepository(pg_conn)


def make_book(**overrides) -> Book:
    work = Work(
        author=overrides.pop("author", "George Orwell"),
        title=overrides.pop("title", "1984"),
        year=overrides.pop("year", 1949),
        genre=overrides.pop("genre", "Dystopian"),
        is_read=overrides.pop("is_read", True),
    )
    defaults = dict(
        work=work,
        format_type=FormatType.PRINT,
        isbn="978-0451524935",
        pages=328,
        duration_minutes=None,
        narrator=None,
    )
    return Book(**{**defaults, **overrides})


class TestPgBookRepositoryAdd:

    def test_add_and_list(self, repo):
        b = make_book()
        repo.add(b)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == b

    def test_add_duplicate_raises(self, repo):
        b = make_book()
        repo.add(b)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(b)


class TestPgBookRepositoryRemove:

    def test_remove_existing(self, repo):
        b = make_book()
        repo.add(b)
        repo.remove(b)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_book())


class TestPgBookRepositoryFind:

    def test_find_by_format_type(self, repo):
        b1 = make_book(format_type=FormatType.PRINT)
        b2 = make_book(format_type=FormatType.EBOOK, isbn="9780000000026")
        repo.add(b1)
        repo.add(b2)
        results = repo.find(format_type=FormatType.PRINT)
        assert len(results) == 1
        assert results[0].format_type == FormatType.PRINT

    def test_find_no_filters_returns_all(self, repo):
        b1 = make_book(format_type=FormatType.PRINT)
        b2 = make_book(format_type=FormatType.EBOOK, isbn="9780000000026")
        repo.add(b1)
        repo.add(b2)
        assert len(repo.find()) == 2

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")
