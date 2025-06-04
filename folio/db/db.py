# db.py
from sqlmodel import create_engine, Session, SQLModel

DATABASE_NAME = "folio.db"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL, echo=False)


class SessionManager:
    """Context manager for database sessions with optional session passing"""

    def __init__(self, session=None):
        self.session = session
        self.owns_session = session is None

    def __enter__(self):
        if self.owns_session:
            self.session = _get_session().__enter__()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.owns_session and self.session:
            self.session.__exit__(exc_type, exc_val, exc_tb)


def _get_session():
    """Return a new SQLModel session"""
    return Session(engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
