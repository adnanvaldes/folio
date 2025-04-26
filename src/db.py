# db.py
from sqlmodel import create_engine, Session

DATABASE_NAME = "folio.db"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL)


def get_session():
    """Return a new SQLModel session"""
    return Session(engine)
