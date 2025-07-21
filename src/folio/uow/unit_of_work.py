from abc import ABC, abstractmethod
import sqlite3


class UnitOfWork(ABC):

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self._cleanup()

    @abstractmethod
    def _start(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class SQLiteUnitOfWork(UnitOfWork):

    def __init__(self, db_path="folio.db"):
        self.db_path = db_path

    def _start(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("BEGIN")
        return self

    def commit(self):
        self.conn.execute("COMMIT")

    def rollback(self):
        self.conn.execute("ROLLBACK")

    def _cleanup(self):
        self.conn.close()
