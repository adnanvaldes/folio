import pytest
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from db.query_builder import QueryBuilder


class BookTest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    year: int
    pages: int
    is_read: bool


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Seed data
        books = [
            BookTest(
                title="Dune", author="Frank Herbert", year=1965, pages=412, is_read=True
            ),
            BookTest(
                title="Foundation",
                author="Isaac Asimov",
                year=1951,
                pages=244,
                is_read=False,
            ),
            BookTest(
                title="Neuromancer",
                author="William Gibson",
                year=1984,
                pages=271,
                is_read=True,
            ),
        ]
        session.add_all(books)
        session.commit()
        yield session


def test_text_exact_match(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.text_filter(BookTest.title, ["foundation"]).run()
    assert len(results) == 1
    assert results[0].author == "Isaac Asimov"


def test_text_partial_match(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.text_filter(BookTest.title, ["dun"], partial=True).run()
    assert len(results) == 1
    assert results[0].title == "Dune"


def test_exact_match_filter(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.exact_match(BookTest.is_read, True).run()
    assert len(results) == 2
    titles = {book.title for book in results}
    assert "Dune" in titles and "Neuromancer" in titles


def test_range_min(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.range_filter(BookTest.year, min_value=1960).run()
    assert len(results) == 2  # Dune and Neuromancer


def test_range_max(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.range_filter(BookTest.year, max_value=1970).run()
    assert len(results) == 2  # Dune and Foundation


def test_range_min_max(session):
    qb = QueryBuilder(session, BookTest)
    results = qb.range_filter(BookTest.year, min_value=1951, max_value=1970).run()
    assert len(results) == 2  # Dune and Foundation


def test_range_exact_val(session):
    qb = QueryBuilder(session, BookTest)
    res_1 = qb.range_filter(BookTest.year, exact_value=[2000]).run()
    qb.reset()
    res_2 = qb.range_filter(BookTest.year, exact_value=[1984]).run()

    assert len(res_1) == 0
    assert len(res_2) == 1


def test_reset(session):
    qb = QueryBuilder(session, BookTest)

    results_1 = qb.range_filter(BookTest.year, exact_value=[1984]).run()
    assert qb.filters_applied == 1

    qb.reset()
    assert qb.filters_applied == 0


def test_combined_filters(session):
    qb = QueryBuilder(session, BookTest)
    results = (
        qb.text_filter(BookTest.author, "gibson")
        .exact_match(BookTest.is_read, True)
        .range_filter(BookTest.pages, min_value=200, max_value=300)
        .run()
    )
    assert len(results) == 1
    assert results[0].title == "Neuromancer"
