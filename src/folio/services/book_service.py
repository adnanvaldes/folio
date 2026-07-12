from folio.models import Book
from folio.uow import UnitOfWork


class BookService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, book: Book) -> None:
        with self.uow:
            if not self.uow.work.find(
                author=book.work.author,
                title=book.work.title,
                year=book.work.year,
            ):
                self.uow.work.add(book.work)
            self.uow.book.add(book)

    def remove(self, book: Book) -> None:
        with self.uow:
            self.uow.book.remove(book)

    def replace(self, old: Book, new: Book) -> None:
        with self.uow:
            self.uow.book.replace(old, new)

    def find(self, **filters) -> list[Book]:
        with self.uow:
            return self.uow.book.find(**filters)

    def list_all(self) -> list[Book]:
        with self.uow:
            return self.uow.book.list_all()
