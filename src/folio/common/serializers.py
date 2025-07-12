import json
from dataclasses import asdict
from typing import Dict, Any, Generic, TypeVar, Type
from abc import ABC, abstractmethod


T = TypeVar("T")


class SerializeStrategy(Generic[T], ABC):

    @abstractmethod
    def serialize(self, record: T) -> Any: ...

    @abstractmethod
    def deserialize(self, data: Any, cls: Type[T]) -> T: ...


class DictSerializer(SerializeStrategy[T]):
    def serialize(self, record: T) -> Dict[str, Any]:
        return asdict(record)

    def deserialize(self, data: Dict[str, Any], cls: Type[T]) -> T:
        # TODO add logic to deal with extra or missing data
        return cls(**data)


class JSONSerializer(SerializeStrategy[T]):
    def serialize(self, record: T) -> str:
        return json.dumps(asdict(record))

    def deserialize(self, data: str, cls: Type[T]) -> T:
        # TODO add logic to deal with extra or missing data
        dict_data = json.loads(data)
        return cls(**dict_data)
