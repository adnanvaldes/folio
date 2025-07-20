from typing import Optional

from folio.repositories import Repository, R


class SQLiteRepository(Repository[R]):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def add(self, record: R) -> int: ...

    @abstractmethod
    def get(self, id: int) -> Optional[R]: ...

    @abstractmethod
    def ensure_table(self) -> None: ...
