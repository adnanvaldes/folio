from typing import Optional, List, Dict
from folio.repositories import Repository, R
from folio.models import Travel


class FakeRepository(Repository[R]):
    def __init__(self):
        self._data: Dict[int, R] = {}
        self._next_id = 1

    def add(self, record: R) -> None:
        self._data[self._next_id] = record
        self._next_id += 1

    def get(self, record_id: int) -> Optional[R]:
        return self._data.get(record_id)

    def list(self) -> List[R]:
        return list(self._data.values())

    def find(self, **kwargs) -> List[R]:
        result = self.list()
        for key, value in kwargs.items():
            result = [r for r in result if getattr(r, key) == value]
        return result

    def _ensure_table(self) -> None:
        pass


class FakeTravelRepository(FakeRepository[Travel]): ...
