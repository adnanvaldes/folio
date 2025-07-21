from abc import ABC, abstractmethod


class UnitOfWork(ABC):

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
