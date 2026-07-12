from folio.models import Book
from folio.uow import UnitOfWork


class BookService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, book: Book) -> None:
        with self.uow:
            existing = self.uow.work.find(
                author=book.work.author,
                title=book.work.title,
                year=book.work.year,
            )
            if not existing:
                self.uow.work.add(book.work)
            else:
                existing_work = existing[0]
                genre = (
                    book.work.genre
                    if book.work.genre is not None and existing_work.genre is None
                    else None
                )
                is_read = (
                    True if book.work.is_read and not existing_work.is_read else None
                )
                if genre is not None or is_read is not None:
                    self.uow.work.update(existing_work, genre=genre, is_read=is_read)
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
