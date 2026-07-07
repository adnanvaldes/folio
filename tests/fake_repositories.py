from typing import List

from folio.repositories.base import AddressRepository
from folio.models.address import Address


class FakeAddressRepository(AddressRepository):

    def __init__(self):
        self._data: set[Address] = set()

    def list(self) -> list[Address]:
        return sorted(self._data)

    def add(self, address: Address) -> None:
        if address in self._data:
            raise ValueError(f"Address already exists: {address}")
        self._data.add(address)

    def remove(self, address: Address) -> None:
        if address not in self._data:
            raise ValueError(f"Address not found: {address}")
        self._data.discard(address)

    def replace(self, old: Address, new: Address) -> None:
        if old not in self._data:
            raise ValueError(f"Address not found: {old}")
        self._data.discard(old)
        self._data.add(new)

    def find(self, **filters) -> List[Address]:
        invalid = set(filters) - self.VALID_FIELDS
        if invalid:
            raise ValueError(f"Invalid filter fields: {invalid}")

        results = set(self._data)
        for field, value in filters.items():
            results = {
                a for a in results
                if getattr(a, field) == value
            }
        return sorted(results)
