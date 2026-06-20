import pytest

from folio.models import Work
from folio.services import WorkService


@pytest.fixture
def populated_work_service(fake_uow):
    service = WorkService(fake_uow)
    service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )
    service.add(
        title="Hyperion", author="Dan Simmons", year=1989, genre="SciFi", is_read=True
    )
    service.add(
        title="The Hobbit",
        author="J.R.R. Tolkien",
        year=1937,
        genre="Fantasy",
        is_read=False,
    )
    return service


def test_add_and_list_work(fake_uow):
    service = WorkService(fake_uow)

    new_id = service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )

    works = service.list()
    assert len(works) == 1
    work = works[0]
    assert isinstance(work, Work)
    assert work.title == "Dune"
    assert work.author == "Frank Herbert"
    assert work.year == 1965
    assert work.genre == "SciFi"
    assert work.is_read is True
    assert new_id == 1


def test_prevents_duplicate_works(fake_uow):
    service = WorkService(fake_uow)
    service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )

    with pytest.raises(ValueError) as exc_info:
        service.add(title="Dune", author="Frank Herbert", year=1965, is_read=False)

    assert "already exists" in str(exc_info.value)


def test_find_by_title(populated_work_service):
    results = populated_work_service.find(title="Dune")
    assert len(results) == 1
    assert results[0].author == "Frank Herbert"


def test_find_by_author(populated_work_service):
    results = populated_work_service.find(author="Dan Simmons")
    assert len(results) == 1
    assert results[0].title == "Hyperion"


def test_find_by_year(populated_work_service):
    results = populated_work_service.find(year=1937)
    assert len(results) == 1
    assert results[0].title == "The Hobbit"


def test_find_by_genre(populated_work_service):
    results = populated_work_service.find(genre="SciFi")
    titles = {w.title for w in results}
    assert titles == {"Dune", "Hyperion"}


def test_find_by_is_read(populated_work_service):
    results = populated_work_service.find(is_read=True)
    assert {w.title for w in results} == {"Dune", "Hyperion"}

    results_unread = populated_work_service.find(is_read=False)
    assert {w.title for w in results_unread} == {"The Hobbit"}


def test_find_by_multiple_fields(populated_work_service):
    results = populated_work_service.find(genre="SciFi", author="Frank Herbert")
    assert len(results) == 1
    assert results[0].title == "Dune"
