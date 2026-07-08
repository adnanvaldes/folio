import pytest
from folio.models.book import Book, FormatType
from folio.models.work import Work
from folio.services.book_service import BookService
from folio.services.work_service import WorkService
from folio.uow import BookSQLiteUoW, WorkSQLiteUoW


A_WORK = Work(author="Brandon Sanderson", title="The Way of Kings", year=2010, genre="Fantasy", is_read=True)


@pytest.fixture
def service(fake_db):
    work_uow = WorkSQLiteUoW(fake_db)
    book_uow = BookSQLiteUoW(fake_db)
    return BookService(book_uow, WorkService(work_uow))


def make_book(**overrides) -> Book:
    defaults = dict(
        work=A_WORK,
        format_type=FormatType.PRINT,
        isbn="978-0-7653-2635-5",
        pages=1007,
    )
    return Book(**{**defaults, **overrides})


class TestBookServiceIntegration:

    def test_add_and_list(self, service):
        book = make_book()
        service.add(book)
        assert book in service.list()

    def test_work_auto_created(self, service):
        new_work = Work(author="New Author", title="New Book", year=2020, genre="Fiction", is_read=False)
        book = make_book(work=new_work)
        service.add(book)
        assert book in service.list()

    def test_null_isbn_survives_round_trip(self, service):
        book = make_book(isbn=None)
        service.add(book)
        retrieved = service.list()[0]
        assert retrieved.isbn is None

    def test_null_narrator_survives_round_trip(self, service):
        book = make_book()
        service.add(book)
        retrieved = service.list()[0]
        assert retrieved.narrator is None

    def test_find_isbn_none_uses_is_null_in_sql(self, service):
        b1 = make_book(isbn=None)
        b2 = make_book(isbn="978-0-0000-0000-0")
        service.add(b1)
        service.add(b2)

        results = service.find(isbn=None)
        assert len(results) == 1
        assert results[0] == b1

    def test_find_by_format_type_as_enum(self, service):
        b1 = make_book()
        b2 = make_book(format_type=FormatType.EBOOK, isbn="978-0-0000-0000-0")
        service.add(b1)
        service.add(b2)

        results = service.find(format_type=FormatType.PRINT)
        assert len(results) == 1
        assert results[0] == b1

    def test_transaction_rolls_back_on_failure(self, service):
        book = make_book()
        service.add(book)

        with pytest.raises(ValueError):
            service.add(book)

        assert len(service.list()) == 1

    def test_remove_persists(self, service):
        book = make_book()
        service.add(book)
        service.remove(book)
        assert service.list() == []

    def test_replace_persists(self, service):
        original = make_book()
        service.add(original)

        corrected = make_book(isbn="978-0-0000-0000-0")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].isbn == "978-0-0000-0000-0"
