from typing import Optional

from folio.repositories import Repository, R


class SQLiteRepository(Repository[R]):
    def __init__(self, session):
        self.session = session

    def add(self, record: R) -> int:
        pass

    def get(self, id: int) -> Optional[R]:
        pass
