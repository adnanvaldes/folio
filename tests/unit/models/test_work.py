import dataclasses

import pytest

from folio.models import Work


def make_work(**overrides) -> Work:
    defaults = dict(
        author="George Orwell",
        title="1984",
        year=1949,
        genre="Dystopian",
        is_read=True,
    )
    return Work(**{**defaults, **overrides})


class TestWorkConstruction:

    def test_valid_work_constructs(self):
        w = make_work()
        assert w.author == "George Orwell"
        assert w.title == "1984"
        assert w.year == 1949
        assert w.genre == "Dystopian"
        assert w.is_read is True

    def test_empty_author_raises(self):
        with pytest.raises(ValueError, match="Author is required"):
            make_work(author="")

    def test_whitespace_author_raises(self):
        with pytest.raises(ValueError, match="Author is required"):
            make_work(author="   ")

    def test_empty_title_raises(self):
        with pytest.raises(ValueError, match="Title is required"):
            make_work(title="")

    def test_whitespace_title_raises(self):
        with pytest.raises(ValueError, match="Title is required"):
            make_work(title="   ")

    def test_year_none_allowed(self):
        w = make_work(year=None)
        assert w.year is None

    def test_rejects_non_int_year(self):
        with pytest.raises(TypeError, match="year must be an int or None"):
            make_work(year="1949")

    def test_genre_none_allowed(self):
        w = make_work(genre=None)
        assert w.genre is None


class TestWorkImmutability:

    def test_cannot_mutate_author(self):
        w = make_work()
        with pytest.raises(dataclasses.FrozenInstanceError):
            w.author = "New Author"

    def test_cannot_mutate_title(self):
        w = make_work()
        with pytest.raises(dataclasses.FrozenInstanceError):
            w.title = "New Title"

    def test_cannot_mutate_is_read(self):
        w = make_work()
        with pytest.raises(dataclasses.FrozenInstanceError):
            w.is_read = False


class TestWorkIdentity:

    def test_equal_works_are_equal(self):
        w1 = make_work()
        w2 = make_work()
        assert w1 == w2

    def test_equal_works_have_same_hash(self):
        w1 = make_work()
        w2 = make_work()
        assert hash(w1) == hash(w2)

    def test_different_author_not_equal(self):
        w1 = make_work(author="Orwell")
        w2 = make_work(author="Huxley")
        assert w1 != w2

    def test_different_title_not_equal(self):
        w1 = make_work(title="1984")
        w2 = make_work(title="Animal Farm")
        assert w1 != w2

    def test_different_year_not_equal(self):
        w1 = make_work(year=1949)
        w2 = make_work(year=1950)
        assert w1 != w2

    def test_year_none_vs_int_not_equal(self):
        w1 = make_work(year=None)
        w2 = make_work(year=1949)
        assert w1 != w2

    def test_different_genre_still_equal(self):
        w1 = make_work(genre="Dystopian")
        w2 = make_work(genre="Science fiction")
        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_different_is_read_still_equal(self):
        w1 = make_work(is_read=True)
        w2 = make_work(is_read=False)
        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_not_equal_to_string(self):
        w = make_work()
        assert w != "1984 by Orwell"

    def test_not_equal_to_none(self):
        w = make_work()
        assert w is not None

    def test_usable_as_dict_key(self):
        w = make_work()
        d = {w: "value"}
        assert d[make_work()] == "value"

    def test_usable_in_set(self):
        w1 = make_work()
        w2 = make_work()
        s = {w1, w2}
        assert len(s) == 1

    def test_case_insensitive_identity(self):
        w1 = make_work(author="george orwell", title="1984")
        w2 = make_work(author="George Orwell", title="1984")
        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_stripped_identity(self):
        w1 = make_work(author="  George Orwell  ", title="  1984  ")
        w2 = make_work(author="George Orwell", title="1984")
        assert w1 == w2
        assert hash(w1) == hash(w2)

    def test_original_casing_preserved(self):
        w = make_work(author="george orwell")
        assert w.author == "george orwell"


class TestWorkOrdering:

    def test_sorts_by_author_then_title_then_year(self):
        w1 = make_work(author="Z", title="A", year=2000)
        w2 = make_work(author="A", title="Z", year=2000)
        w3 = make_work(author="A", title="A", year=1999)
        w4 = make_work(author="A", title="A", year=2000)
        assert sorted([w1, w2, w3, w4]) == [w3, w4, w2, w1]

    def test_case_insensitive_ordering(self):
        w1 = make_work(author="a", title="a")
        w2 = make_work(author="B", title="B")
        assert sorted([w2, w1]) == [w1, w2]


class TestWorkStr:

    def test_str_read(self):
        w = make_work(is_read=True)
        s = str(w)
        assert "Read" in s

    def test_str_not_read(self):
        w = make_work(is_read=False)
        s = str(w)
        assert "Not read" in s

    def test_str_contains_details(self):
        w = make_work()
        s = str(w)
        assert "1984" in s
        assert "Orwell" in s
