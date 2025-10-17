import pytest
import sqlite3

from folio.services import WorkService
from folio.uow import WorkSQliteUoW
from folio.repositories import SQLiteWorkRepository


def test_add_and_list_work(fake_db):
    uow = WorkSQliteUoW(fake_db)
    service = WorkService(uow)

    service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )
    works = service.list()

    assert len(works) == 1

    work = works[0]
    assert work.title == "Dune"
    assert work.author == "Frank Herbert"
    assert work.year == 1965
    assert work.genre == "SciFi"
    assert work.is_read is True


def test_get_work_by_id(fake_db):
    uow = WorkSQLiteUoW(fake_db)
    service = WorkService(uow)
    service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )

    work_id = 1
    work = service.get(work_id)

    assert work is not None
    assert work.title == "Dune"
    assert work.author == "Frank Herbert"
    assert work.year == 1965


def test_prevent_duplicate_work(fake_db):
    uow = WorkSQLiteUoW(fake_db)
    service = WorkService(uow)
    service.add(
        title="Dune", author="Frank Herbert", year=1965, genre="SciFi", is_read=True
    )

    with pytest.raises(ValueError) as e:
        service.add(title="Dune", author="Frank Herbert", year=1965)

    assert "already exists" in str(e.value)


def test_find_work_by_filters(fake_db):
    uow = WorkSQliteUoW(fake_db)
    service = WorkService(uow)

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

    results = service.find(title="Dune")
    assert len(results) == 1
    assert results[0].title == "Dune"

    results = service.find(is_read=True)
    assert len(results) == 2
    titles = {w.title for w in results}
    assert titles == {"Dune", "Hyperion"}

    results = service.find(genre="SciFi", year=1965)
    assert len(results) == 1
    assert results[0].title == "Dune"
