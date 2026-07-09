import dataclasses
from typing import List

from folio.models import Work
from folio.uow import UnitOfWork


class WorkService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, work: Work) -> None:
        with self.uow:
            self.uow.work.add(work)

    def remove(self, work: Work, *, force: bool = False) -> None:
        with self.uow:
            book_repo = getattr(self.uow, "book", None)
            if book_repo is not None:
                refs = book_repo.find(
                    author=work.author, title=work.title, year=work.year
                )
                if refs:
                    if not force:
                        raise ValueError(
                            f"Work '{work}' is referenced by {len(refs)} book(s); "
                            f"use remove(work, force=True) to also remove "
                            f"associated books"
                        )
                    for book in refs:
                        book_repo.remove(book)
            self.uow.work.remove(work)

    def replace(self, old: Work, new: Work) -> None:
        with self.uow:
            book_repo = getattr(self.uow, "book", None)
            if book_repo is not None:
                refs = book_repo.find(author=old.author, title=old.title, year=old.year)
                updated = [dataclasses.replace(b, work=new) for b in refs]
                for old_book in refs:
                    book_repo.remove(old_book)
            self.uow.work.replace(old, new)
            if book_repo is not None:
                for new_book in updated:
                    book_repo.add(new_book)

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        with self.uow:
            self.uow.work.update(work, genre=genre, is_read=is_read)

    def find(self, **filters) -> List[Work]:
        with self.uow:
            return self.uow.work.find(**filters)

    def list(self) -> list[Work]:
        with self.uow:
            return self.uow.work.list()
