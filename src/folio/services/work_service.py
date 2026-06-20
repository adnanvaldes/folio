from typing import List, Optional

from folio.models import Work
from folio.uow import UnitOfWork


class WorkService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(
        self,
        author: str,
        title: str,
        year: int = None,
        genre: str = None,
        is_read: bool = True,
    ) -> int:

        if self.find(author=author, title=title, year=year):
            raise ValueError(f"Work already exists for {author, title, year}")

        work = Work(author=author, title=title, year=year, genre=genre, is_read=is_read)

        with self.uow:
            new_id = self.uow.work.add(work)
            return new_id

    def get(self, work_id: int) -> Optional[Work]:
        with self.uow:
            return self.uow.work.get(work_id)

    def list(self) -> List[Work]:
        with self.uow:
            return self.uow.work.list()

    def find(
        self,
        author: str | None = None,
        title: str | None = None,
        year: int | None = None,
        genre: str | None = None,
        is_read: bool | None = None,
    ) -> List[Work]:
        data = {
            "author": author.strip() if author else None,
            "title": title.strip() if title else None,
            "year": year if year is not None else None,
            "genre": genre.strip() if genre else None,
            "is_read": is_read if is_read is not None else None,
        }

        with self.uow:
            return self.uow.work.find(**data)
