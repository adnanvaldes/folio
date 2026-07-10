from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from folio.repositories import (
        AddressRepository,
        BookRepository,
        EducationRepository,
        EmploymentRepository,
        TravelRepository,
        WorkRepository,
    )


class UnitOfWork(ABC):

    @property
    def travel(self) -> TravelRepository:
        return getattr(self, "_travel")

    @property
    def addresses(self) -> AddressRepository:
        return getattr(self, "_addresses")

    @property
    def education(self) -> EducationRepository:
        return getattr(self, "_education")

    @property
    def employment(self) -> EmploymentRepository:
        return getattr(self, "_employment")

    @property
    def work(self) -> WorkRepository:
        return getattr(self, "_work")

    @property
    def book(self) -> BookRepository:
        return getattr(self, "_book")

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self._cleanup()

    @abstractmethod
    def _start(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def _cleanup(self):
        pass
