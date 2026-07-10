import pytest

from folio.models import Book, FormatType, Work
from folio.services import BookService

A_WORK = Work(
    author="Brandon Sanderson",
    title="The Way of Kings",
    year=2010,
    genre="Fantasy",
    is_read=True,
)


def make_book(**overrides) -> Book:
    defaults = dict(
        work=A_WORK,
        format_type=FormatType.PRINT,
        isbn="9780765326355",
        pages=1007,
    )
    return Book(**{**defaults, **overrides})


@pytest.fixture
def service(fake_uow):
    return BookService(fake_uow)


class TestAdd:

    def test_add_single_book(self, service):
        book = make_book()
        service.add(book)
        assert book in service.list_all()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_book())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        book = make_book()
        service.add(book)
        with pytest.raises(ValueError, match="already exists"):
            service.add(book)

    def test_add_auto_creates_work(self, service, fake_uow):
        new_work = Work(
            author="New Author",
            title="New Book",
            year=2020,
            genre="Fiction",
            is_read=False,
        )
        book = make_book(work=new_work)
        service.add(book)
        assert new_work in fake_uow.work.list_all()

    def test_add_reuses_existing_work(self, service, fake_uow):
        fake_uow.work.add(A_WORK)
        book = make_book()
        service.add(book)
        assert len(fake_uow.work.list_all()) == 1


class TestRemove:

    def test_remove_existing_book(self, service):
        book = make_book()
        service.add(book)
        service.remove(book)
        assert service.list_all() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_book())


class TestReplace:

    def test_replace_updates_book(self, service):
        original = make_book()
        service.add(original)

        corrected = make_book(isbn="9780000000026")
        service.replace(original, corrected)

        result = service.list_all()
        assert len(result) == 1
        assert result[0].isbn == "9780000000026"

    def test_replace_nonexistent_raises(self, service):
        original = make_book()
        other = make_book(isbn="9780000000026")
        with pytest.raises(ValueError, match="not found"):
            service.replace(original, other)


class TestFind:

    def test_find_by_author(self, service):
        b1 = make_book()
        other_work = Work(
            author="Robert Jordan",
            title="The Eye of the World",
            year=1990,
            genre="Fantasy",
            is_read=True,
        )
        b2 = make_book(work=other_work, isbn="9780000000026")
        service.add(b1)
        service.add(b2)

        results = service.find(author="Brandon Sanderson")
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_title(self, service):
        b1 = make_book()
        other_work = Work(
            author="Brandon Sanderson",
            title="Words of Radiance",
            year=2014,
            genre="Fantasy",
            is_read=True,
        )
        b2 = make_book(
            work=other_work,
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000026",
        )
        service.add(b1)
        service.add(b2)

        results = service.find(title="The Way of Kings")
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_format_type(self, service):
        b1 = make_book()
        b2 = make_book(format_type=FormatType.EBOOK, isbn="9780000000026")
        service.add(b1)
        service.add(b2)

        results = service.find(format_type=FormatType.PRINT)
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_isbn(self, service):
        b1 = make_book()
        b2 = make_book(isbn="9780000000026")
        service.add(b1)
        service.add(b2)

        results = service.find(isbn="9780765326355")
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_narrator_is_none(self, service):
        b1 = make_book()
        b2 = make_book(
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000026",
            narrator="Michael Kramer",
        )
        service.add(b1)
        service.add(b2)

        results = service.find(narrator=None)
        assert len(results) == 1
        assert results[0] == b1

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent_field="value")


class TestList:

    def test_list_empty(self, service):
        assert service.list_all() == []

    def test_list_returns_all_books(self, service):
        b1 = make_book()
        b2 = make_book(isbn="9780000000026")
        service.add(b1)
        service.add(b2)

        result = service.list_all()
        assert len(result) == 2
        assert b1 in result
        assert b2 in result
