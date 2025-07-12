from folio.repositories.base import Repository
from folio.models import Book


class BookRepository(Repository[Book]): ...
