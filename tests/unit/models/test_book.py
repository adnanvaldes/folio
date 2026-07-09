import dataclasses

import pytest

from folio.models import Book, FormatType, Work

A_WORK = Work(
    author="Brandon Sanderson",
    title="The Way of Kings",
    year=2010,
    genre="Fantasy",
    is_read=True,
)
AUDIO_WORK = Work(
    author="Brandon Sanderson",
    title="Words of Radiance",
    year=2014,
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


class TestBookConstruction:

    def test_valid_print_book_constructs(self):
        book = make_book()
        assert book.work == A_WORK
        assert book.format_type == FormatType.PRINT
        assert book.isbn == "9780765326355"
        assert book.pages == 1007

    def test_valid_audio_book_constructs(self):
        book = make_book(
            work=AUDIO_WORK,
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
        )
        assert book.format_type == FormatType.AUDIO
        assert book.duration_minutes == 552
        assert book.pages is None

    def test_valid_ebook_constructs(self):
        book = make_book(format_type=FormatType.EBOOK, pages=800, isbn="9780123456786")
        assert book.format_type == FormatType.EBOOK
        assert book.pages == 800

    def test_audio_book_requires_duration(self):
        with pytest.raises(
            ValueError, match="duration_minutes is required for audio books"
        ):
            make_book(format_type=FormatType.AUDIO, pages=None, isbn="9780000000019")

    def test_text_book_requires_pages(self):
        with pytest.raises(ValueError, match="pages is required for text books"):
            make_book(pages=None)

    def test_strips_isbn_whitespace(self):
        book = make_book(isbn="  978-0-7653-2635-5  ")
        assert book.isbn == "9780765326355"

    def test_isbn_empty_string_normalized_to_none(self):
        book = make_book(isbn="")
        assert book.isbn is None

    def test_isbn_whitespace_only_normalized_to_none(self):
        book = make_book(isbn="   ")
        assert book.isbn is None

    def test_isbn_none_remains_none(self):
        book = make_book(isbn=None)
        assert book.isbn is None

    def test_strips_narrator_whitespace(self):
        book = make_book(
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
            narrator="  Michael Kramer  ",
        )
        assert book.narrator == "Michael Kramer"

    def test_narrator_empty_string_normalized_to_none(self):
        book = make_book(
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
            narrator="",
        )
        assert book.narrator is None

    def test_narrator_none_remains_none(self):
        book = make_book()
        assert book.narrator is None

    def test_rejects_non_work(self):
        with pytest.raises(TypeError, match="work must be a Work"):
            Book(
                work="not a work",
                format_type=FormatType.PRINT,
                isbn="9780765326355",
                pages=1007,
            )

    def test_rejects_non_format_type(self):
        with pytest.raises(TypeError, match="format_type must be a FormatType"):
            Book(work=A_WORK, format_type="print", isbn="9780765326355", pages=1007)

    def test_rejects_non_int_pages(self):
        with pytest.raises(TypeError, match="pages must be an int or None"):
            make_book(pages="1007")

    def test_rejects_non_int_duration(self):
        with pytest.raises(TypeError, match="duration_minutes must be an int or None"):
            make_book(
                format_type=FormatType.AUDIO,
                pages=None,
                duration_minutes=552.5,
                isbn="9780000000019",
            )


class TestBookImmutability:

    def test_cannot_mutate_work(self):
        book = make_book()
        with pytest.raises(dataclasses.FrozenInstanceError):
            book.work = AUDIO_WORK

    def test_cannot_mutate_format_type(self):
        book = make_book()
        with pytest.raises(dataclasses.FrozenInstanceError):
            book.format_type = FormatType.EBOOK

    def test_cannot_mutate_isbn(self):
        book = make_book()
        with pytest.raises(dataclasses.FrozenInstanceError):
            book.isbn = "9780000000026"


class TestBookIdentity:

    def test_equal_books_are_equal(self):
        b1 = make_book()
        b2 = make_book()
        assert b1 == b2

    def test_equal_books_have_same_hash(self):
        b1 = make_book()
        b2 = make_book()
        assert hash(b1) == hash(b2)

    def test_case_insensitive_equality_via_work(self):
        work1 = Work(
            author="Brandon Sanderson",
            title="The Way of Kings",
            year=2010,
            genre="Fantasy",
            is_read=True,
        )
        work2 = Work(
            author="brandon sanderson",
            title="the way of kings",
            year=2010,
            genre="Fantasy",
            is_read=True,
        )
        b1 = make_book(work=work1)
        b2 = make_book(work=work2)
        assert b1 == b2

    def test_case_insensitive_isbn_equality(self):
        b1 = make_book(isbn="9780765326355")
        b2 = make_book(isbn="9780765326355")
        assert b1 == b2

    def test_different_work_not_equal(self):
        other_work = Work(
            author="Robert Jordan",
            title="The Eye of the World",
            year=1990,
            genre="Fantasy",
            is_read=True,
        )
        b1 = make_book()
        b2 = make_book(work=other_work)
        assert b1 != b2

    def test_different_format_not_equal(self):
        b1 = make_book(format_type=FormatType.PRINT)
        b2 = make_book(format_type=FormatType.EBOOK, isbn="9780000000026")
        assert b1 != b2

    def test_different_isbn_not_equal(self):
        b1 = make_book(isbn="9780765326355")
        b2 = make_book(isbn="9780000000026")
        assert b1 != b2

    def test_not_equal_to_string(self):
        book = make_book()
        assert book != "not a book"

    def test_not_equal_to_none(self):
        book = make_book()
        assert book is not None

    def test_usable_as_dict_key(self):
        book = make_book()
        d = {book: "value"}
        assert d[make_book()] == "value"

    def test_usable_in_set(self):
        b1 = make_book()
        b2 = make_book()
        s = {b1, b2}
        assert len(s) == 1


class TestBookOrdering:

    def test_orders_by_author_then_title_then_year_then_format_then_isbn(self):
        b1 = make_book(
            work=Work(
                author="A Author",
                title="Best Book",
                year=2000,
                genre="Fiction",
                is_read=True,
            ),
            isbn="9780000000033",
        )
        b2 = make_book(
            work=Work(
                author="B Author",
                title="Another Book",
                year=2000,
                genre="Fiction",
                is_read=True,
            ),
            isbn="9780000000040",
        )
        assert b1 < b2

    def test_different_format_orders_by_format_value(self):
        b1 = make_book(
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=500,
            isbn="9780000000033",
        )
        b2 = make_book(format_type=FormatType.PRINT, isbn="9780000000040")
        assert b1 < b2  # "audio" < "print"

    def test_sorted_orders_correctly(self):
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
        assert sorted([b1, b2]) == [b2, b1]

    def test_ordering_fields_returns_tuple(self):
        book = make_book()
        expected = (
            *book.work._ordering_fields(),
            book.format_type.value,
            (book.isbn or "").lower().strip(),
        )
        assert book._ordering_fields() == expected


class TestBookStr:

    def test_str_with_isbn(self):
        book = make_book()
        assert (
            str(book) == "The Way of Kings by Brandon Sanderson (print, 9780765326355)"
        )

    def test_str_without_isbn(self):
        book = make_book(isbn=None)
        assert str(book) == "The Way of Kings by Brandon Sanderson (print, no ISBN)"


class TestBookLength:

    def test_length_returns_pages_for_print(self):
        book = make_book(pages=1007)
        assert book.length == 1007

    def test_length_returns_pages_for_ebook(self):
        book = make_book(format_type=FormatType.EBOOK, pages=800, isbn="9780000000026")
        assert book.length == 800

    def test_length_returns_duration_for_audio(self):
        book = make_book(
            format_type=FormatType.AUDIO,
            pages=None,
            duration_minutes=552,
            isbn="9780000000019",
        )
        assert book.length == 552
