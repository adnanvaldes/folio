from typing import List

from folio.models.book import Book
from folio.uow import UnitOfWork
from .work_service import WorkService


class BookService:
    def __init__(self, uow: UnitOfWork, work_service: WorkService):
        self.uow = uow
        self.work_service = work_service

    def add(self, book: Book) -> None:
        try:
            self.work_service.add(book.work)
        except ValueError:
            pass
        with self.uow:
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
