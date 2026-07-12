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

    travel: TravelRepository
    addresses: AddressRepository
    education: EducationRepository
    employment: EmploymentRepository
    work: WorkRepository
    book: BookRepository

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
