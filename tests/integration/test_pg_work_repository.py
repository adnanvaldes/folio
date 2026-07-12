import pytest

from folio.exceptions import (
    FolioDuplicateError,
    FolioInvalidFilterError,
    FolioNotFoundError,
)
from folio.models import Work
from folio.repositories import PgWorkRepository


@pytest.fixture
def repo(pg_conn, _pg_drop_tables):
    return PgWorkRepository(pg_conn)


def make_work(**overrides) -> Work:
    defaults = dict(
        author="George Orwell",
        title="1984",
        year=1949,
        genre="Dystopian",
        is_read=True,
    )
    return Work(**{**defaults, **overrides})


class TestPgWorkRepositoryAdd:

    def test_add_and_list(self, repo):
        w = make_work()
        repo.add(w)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0] == w

    def test_add_duplicate_raises(self, repo):
        w = make_work()
        repo.add(w)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(w)

    def test_add_case_insensitive_duplicate_raises(self, repo):
        w1 = make_work(author="George Orwell", title="1984")
        w2 = make_work(author="george orwell", title="1984")
        repo.add(w1)
        with pytest.raises(FolioDuplicateError, match="already exists"):
            repo.add(w2)

    def test_list_returns_sorted(self, repo):
        w1 = make_work(author="Z", title="A", year=2000)
        w2 = make_work(author="A", title="Z", year=2000)
        w3 = make_work(author="A", title="A", year=2000)
        repo.add(w1)
        repo.add(w2)
        repo.add(w3)
        assert repo.list_all() == [w3, w2, w1]


class TestPgWorkRepositoryScalars:

    def test_is_read_round_trips_as_bool(self, repo):
        w = make_work(is_read=True)
        repo.add(w)
        result = repo.list_all()[0]
        assert isinstance(result.is_read, bool)
        assert result.is_read is True

    def test_is_read_false_round_trips(self, repo):
        w = make_work(is_read=False)
        repo.add(w)
        result = repo.list_all()[0]
        assert result.is_read is False

    def test_year_none_round_trips(self, repo):
        w = make_work(year=None)
        repo.add(w)
        result = repo.list_all()[0]
        assert result.year is None


class TestPgWorkRepositoryRemove:

    def test_remove_existing(self, repo):
        w = make_work()
        repo.add(w)
        repo.remove(w)
        assert repo.list_all() == []

    def test_remove_nonexistent_raises(self, repo):
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.remove(make_work())


class TestPgWorkRepositoryReplace:

    def test_replace_updates_record(self, repo):
        original = make_work(genre="Wrong")
        repo.add(original)
        corrected = make_work(genre="Corrected")
        repo.replace(original, corrected)
        result = repo.list_all()
        assert len(result) == 1
        assert result[0].genre == "Corrected"

    def test_replace_nonexistent_raises(self, repo):
        w1 = make_work(author="A", title="B", year=2000)
        w2 = make_work(author="C", title="D", year=2001)
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.replace(w1, w2)


class TestPgWorkRepositoryUpdate:

    def test_update_genre(self, repo):
        w = make_work()
        repo.add(w)
        repo.update(w, genre="Science fiction")
        result = repo.list_all()[0]
        assert result.genre == "Science fiction"

    def test_update_is_read(self, repo):
        w = make_work(is_read=False)
        repo.add(w)
        repo.update(w, is_read=True)
        result = repo.list_all()[0]
        assert result.is_read is True

    def test_update_both(self, repo):
        w = make_work(genre="Dystopian", is_read=False)
        repo.add(w)
        repo.update(w, genre="Sci-Fi", is_read=True)
        result = repo.list_all()[0]
        assert result.genre == "Sci-Fi"
        assert result.is_read is True

    def test_update_no_fields_raises(self, repo):
        from folio.exceptions import FolioValidationError

        w = make_work()
        repo.add(w)
        with pytest.raises(FolioValidationError, match="No fields to update"):
            repo.update(w)

    def test_update_nonexistent_raises(self, repo):
        w = make_work()
        with pytest.raises(FolioNotFoundError, match="not found"):
            repo.update(w, genre="Sci-Fi")


class TestPgWorkRepositoryFind:

    def test_find_by_author(self, repo):
        w1 = make_work(author="George Orwell")
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(author="George Orwell")
        assert len(results) == 1
        assert results[0].author == "George Orwell"

    def test_find_by_author_case_insensitive(self, repo):
        w = make_work(author="George Orwell")
        repo.add(w)
        results = repo.find(author="george orwell")
        assert len(results) == 1

    def test_find_no_filters_returns_all(self, repo):
        w1 = make_work(author="A", title="B")
        w2 = make_work(author="C", title="D", year=2000)
        repo.add(w1)
        repo.add(w2)
        assert len(repo.find()) == 2

    def test_find_by_is_read(self, repo):
        w1 = make_work(is_read=True)
        w2 = make_work(author="A", title="B", year=2000, is_read=False)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(is_read=True)
        assert len(results) == 1
        assert results[0].is_read is True

    def test_find_by_year_none(self, repo):
        w1 = make_work(year=None)
        w2 = make_work(author="A", title="B", year=2000)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(year=None)
        assert len(results) == 1
        assert results[0].year is None

    def test_find_invalid_field_raises(self, repo):
        with pytest.raises(FolioInvalidFilterError, match="Invalid filter fields"):
            repo.find(invalid="x")

    def test_find_year_before(self, repo):
        w1 = make_work(author="A", title="Old", year=1950)
        w2 = make_work(author="B", title="New", year=2020)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(year__before=2000)
        assert len(results) == 1
        assert results[0].title == "Old"

    def test_find_year_after(self, repo):
        w1 = make_work(author="A", title="Old", year=1950)
        w2 = make_work(author="B", title="New", year=2020)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(year__after=2000)
        assert len(results) == 1
        assert results[0].title == "New"

    def test_find_author_contains(self, repo):
        w1 = make_work(author="George Orwell", title="1984")
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        repo.add(w1)
        repo.add(w2)
        results = repo.find(author__contains="orwell")
        assert len(results) == 1
        assert results[0].author == "George Orwell"
