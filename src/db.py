# db.py
from sqlmodel import create_engine, Session, SQLModel

DATABASE_NAME = "folio.db"
DATABASE_URL = f"sqlite:///{DATABASE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Return a new SQLModel session"""
    return Session(engine)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)