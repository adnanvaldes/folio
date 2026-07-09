import pytest

from folio.models import Work
from folio.services import WorkService


def make_work(**overrides) -> Work:
    defaults = dict(
        author="George Orwell",
        title="1984",
        year=1949,
        genre="Dystopian",
        is_read=True,
    )
    return Work(**{**defaults, **overrides})


@pytest.fixture
def service(fake_uow):
    return WorkService(fake_uow)


class TestAdd:

    def test_add_single_work(self, service):
        w = make_work()
        service.add(w)
        assert w in service.list()

    def test_add_commits_transaction(self, service, fake_uow):
        service.add(make_work())
        assert fake_uow.committed is True

    def test_add_duplicate_raises(self, service):
        w = make_work()
        service.add(w)
        with pytest.raises(ValueError, match="already exists"):
            service.add(w)

    def test_add_multiple(self, service):
        w1 = make_work(author="Aldous Huxley", title="Brave New World")
        w2 = make_work(author="George Orwell", title="Animal Farm", year=1945)
        service.add(w1)
        service.add(w2)
        assert len(service.list()) == 2


class TestRemove:

    def test_remove_existing(self, service):
        w = make_work()
        service.add(w)
        service.remove(w)
        assert service.list() == []

    def test_remove_nonexistent_raises(self, service):
        with pytest.raises(ValueError, match="not found"):
            service.remove(make_work())


class TestReplace:

    def test_replace_updates_record(self, service):
        original = make_work(genre="Wrong genre")
        service.add(original)

        corrected = make_work(genre="Corrected genre")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].genre == "Corrected genre"

    def test_replace_nonexistent_raises(self, service):
        w1 = make_work(author="A", title="B", year=2000)
        w2 = make_work(author="C", title="D", year=2001)
        with pytest.raises(ValueError, match="not found"):
            service.replace(w1, w2)


class TestUpdate:

    def test_update_genre(self, service):
        w = make_work()
        service.add(w)
        service.update(w, genre="Science fiction")
        result = service.list()[0]
        assert result.genre == "Science fiction"

    def test_update_is_read(self, service):
        w = make_work(is_read=False)
        service.add(w)
        service.update(w, is_read=True)
        result = service.list()[0]
        assert result.is_read is True

    def test_update_both_fields(self, service):
        w = make_work(genre="Dystopian", is_read=False)
        service.add(w)
        service.update(w, genre="Sci-Fi", is_read=True)
        result = service.list()[0]
        assert result.genre == "Sci-Fi"
        assert result.is_read is True

    def test_update_no_fields_raises(self, service):
        w = make_work()
        service.add(w)
        with pytest.raises(ValueError, match="No fields to update"):
            service.update(w)

    def test_update_nonexistent_raises(self, service):
        w = make_work()
        with pytest.raises(ValueError, match="not found"):
            service.update(w, genre="Sci-Fi")

    def test_update_preserves_identity(self, service):
        w = make_work(
            author="George Orwell", title="1984", year=1949, genre="Dystopian"
        )
        service.add(w)
        service.update(w, genre="Classic")
        result = service.list()
        assert len(result) == 1
        assert result[0].author == "George Orwell"
        assert result[0].title == "1984"
        assert result[0].year == 1949


class TestFind:

    def test_find_by_author(self, service):
        w1 = make_work(author="George Orwell")
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        service.add(w1)
        service.add(w2)

        results = service.find(author="George Orwell")
        assert len(results) == 1
        assert results[0].author == "George Orwell"

    def test_find_by_title(self, service):
        w1 = make_work(title="1984")
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        service.add(w1)
        service.add(w2)

        results = service.find(title="1984")
        assert len(results) == 1

    def test_find_by_year(self, service):
        w1 = make_work(year=1949)
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        service.add(w1)
        service.add(w2)

        results = service.find(year=1949)
        assert len(results) == 1

    def test_find_by_genre(self, service):
        w1 = make_work(genre="Dystopian")
        w2 = make_work(
            author="Aldous Huxley",
            title="Brave New World",
            year=1932,
            genre="Science fiction",
        )
        service.add(w1)
        service.add(w2)

        results = service.find(genre="Dystopian")
        assert len(results) == 1

    def test_find_by_is_read(self, service):
        w1 = make_work(is_read=True)
        w2 = make_work(
            author="Aldous Huxley", title="Brave New World", year=1932, is_read=False
        )
        service.add(w1)
        service.add(w2)

        results = service.find(is_read=False)
        assert len(results) == 1

    def test_find_invalid_field_raises(self, service):
        with pytest.raises(ValueError, match="Invalid filter fields"):
            service.find(nonexistent=True)

    def test_list_returns_all(self, service):
        w1 = make_work(author="A", title="B")
        w2 = make_work(author="C", title="D", year=2000)
        service.add(w1)
        service.add(w2)
        assert len(service.list()) == 2

    def test_list_empty(self, service):
        assert service.list() == []
