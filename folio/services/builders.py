from abc import ABC, abstractmethod


class BaseBuilder[Self: "Builder"](ABC):
    def __init__(self):
        self._build = None

    @abstractmethod
    def build(self) -> Self: ...

    def reset(self) -> None:
        self._built = None
