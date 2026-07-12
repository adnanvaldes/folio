from folio.exceptions import FolioCascadeError
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
            books = self.uow.book.find(
                author=work.author,
                title=work.title,
                year=work.year,
            )
            if books:
                if not force:
                    raise FolioCascadeError(
                        f"Cannot remove {work}: {len(books)} book(s) reference it. "
                        f"Use --force to remove them too."
                    )
                for book in books:
                    self.uow.book.remove(book)
            self.uow.work.remove(work)

    def replace(self, old: Work, new: Work) -> None:
        with self.uow:
            self.uow.work.replace(old, new)

    def update(
        self, work: Work, *, genre: str | None = None, is_read: bool | None = None
    ) -> None:
        with self.uow:
            self.uow.work.update(work, genre=genre, is_read=is_read)

    def find(self, **filters) -> list[Work]:
        with self.uow:
            return self.uow.work.find(**filters)

    def list_all(self) -> list[Work]:
        with self.uow:
            return self.uow.work.list_all()
