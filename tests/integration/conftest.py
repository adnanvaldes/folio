import os

import pytest

PG_DSN = os.environ.get("FOLIO_PG_DSN")


@pytest.fixture
def pg_conn():
    """A live PostgreSQL connection for integration tests.
    Automatically rolls back on teardown.
    """
    if not PG_DSN:
        pytest.skip("FOLIO_PG_DSN not set")
    import psycopg
    import psycopg.rows

    conn = psycopg.connect(PG_DSN)
    conn.row_factory = psycopg.rows.dict_row
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture(autouse=True)
def _pg_drop_tables():
    """Drop and recreate all tables before each PG test for isolation."""
    if not PG_DSN:
        yield
        return
    import psycopg

    conn = psycopg.connect(PG_DSN)
    conn.autocommit = True
    with conn.cursor() as cur:
        for table in ("book", "work", "travel", "address", "education", "employment"):
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    conn.close()
    yield
