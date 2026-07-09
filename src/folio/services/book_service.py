from typing import List

from folio.models import Book
from folio.uow import UnitOfWork


class BookService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, book: Book) -> None:
        with self.uow:
            work_repo = getattr(self.uow, "work", None)
            if work_repo is not None and not work_repo.find(
                author=book.work.author,
                title=book.work.title,
                year=book.work.year,
            ):
                work_repo.add(book.work)
            self.uow.book.add(book)

    def remove(self, book: Book) -> None:
        with self.uow:
            self.uow.book.remove(book)

    def replace(self, old: Book, new: Book) -> None:
        with self.uow:
            self.uow.book.replace(old, new)

    def find(self, **filters) -> List[Book]:
        with self.uow:
            return self.uow.book.find(**filters)

    def list(self) -> list[Book]:
        with self.uow:
            return self.uow.book.list()
