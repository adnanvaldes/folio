import pytest

from folio.models import Work
from folio.services import WorkService
from folio.uow import WorkSQLiteUoW


@pytest.fixture
def service(fake_db):
    uow = WorkSQLiteUoW(fake_db)
    return WorkService(uow)


def make_work(**overrides) -> Work:
    defaults = dict(
        author="George Orwell",
        title="1984",
        year=1949,
        genre="Dystopian",
        is_read=True,
    )
    return Work(**{**defaults, **overrides})


class TestWorkServiceIntegration:

    def test_add_and_list(self, service):
        w = make_work()
        service.add(w)
        result = service.list()
        assert len(result) == 1
        assert result[0] == w

    def test_remove_and_list(self, service):
        w = make_work()
        service.add(w)
        service.remove(w)
        assert service.list() == []

    def test_replace_persists_correctly(self, service):
        original = make_work(genre="Old genre")
        service.add(original)

        corrected = make_work(genre="New genre")
        service.replace(original, corrected)

        result = service.list()
        assert len(result) == 1
        assert result[0].genre == "New genre"

    def test_update_genre_persists(self, service):
        w = make_work()
        service.add(w)
        service.update(w, genre="Updated genre")
        result = service.list()[0]
        assert result.genre == "Updated genre"

    def test_update_is_read_persists(self, service):
        w = make_work(is_read=False)
        service.add(w)
        service.update(w, is_read=True)
        result = service.list()[0]
        assert result.is_read is True

    def test_find_by_author(self, service):
        w1 = make_work(author="George Orwell")
        w2 = make_work(author="Aldous Huxley", title="Brave New World", year=1932)
        service.add(w1)
        service.add(w2)

        results = service.find(author="George Orwell")
        assert len(results) == 1

    def test_transaction_rolls_back_on_failure(self, service):
        w = make_work()
        service.add(w)
        with pytest.raises(ValueError):
            service.add(w)  # duplicate — should rollback
        assert len(service.list()) == 1

    def test_add_multiple_orders_correctly(self, service):
        w1 = make_work(author="Z", title="A", year=2000)
        w2 = make_work(author="A", title="Z", year=2000)
        w3 = make_work(author="A", title="A", year=2000)
        service.add(w1)
        service.add(w2)
        service.add(w3)
        authors = [w.author for w in service.list()]
        assert authors == ["A", "A", "Z"]

    def test_bool_round_trips_correctly(self, service):
        w = make_work(is_read=False)
        service.add(w)
        result = service.list()[0]
        assert result.is_read is False
        assert isinstance(result.is_read, bool)
