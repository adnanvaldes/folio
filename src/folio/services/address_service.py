import datetime as dt
from typing import List, Optional
from folio.models import Address
from folio.uow import UnitOfWork
from folio.common import normalize_date


class AddressService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(
        self,
        street: str,
        city: str,
        country: str,
        postal_code: str,
        start: dt.date,
        end: dt.date | None = None,
        province: str | None = None,
    ) -> int:

        data = {
            "street": street.strip(),
            "city": city.strip(),
            "country": country.strip(),
            "postal_code": postal_code.strip(),
            "start": dt.date.fromisoformat(start) if isinstance(start, str) else start,
            "end": dt.date.fromisoformat(end) if isinstance(end, str) else end,
            "province": province.strip() if province else None,
        }

        if self.find(**data):
            fields = ", ".join(f"{v}" for _, v in data.items())
            raise ValueError(f"Address already already exists for {fields}")

        self._overlaps(data["start"], data["end"])

        address = Address(**data)
        with self.uow:
            new_id = self.uow.address.add(address)
            return new_id

    def get(self, address_id: int) -> Optional[Address]:
        with self.uow:
            return self.uow.address.get(address_id)

    def list(self) -> List[Address]:
        with self.uow:
            return self.uow.address.list()

    def find(
        self,
        street: str | None = None,
        city: str | None = None,
        country: str | None = None,
        postal_code: str | None = None,
        start: dt.date | None = None,
        end: dt.date | None = None,
        province: str | None = None,
    ) -> List[Address]:
        data = {
            "street": street.strip() if street else None,
            "city": city.strip() if city else None,
            "country": country.strip() if country else None,
            "postal_code": postal_code.strip() if postal_code else None,
            "start": dt.date.fromisoformat(start) if isinstance(start, str) else start,
            "end": dt.date.fromisoformat(end) if isinstance(end, str) else end,
            "province": province.strip() if province else None,
        }

        with self.uow:
            return self.uow.address.find(**data)

    def update(
        self,
        key: int,
        street: str | None = None,
        city: str | None = None,
        country: str | None = None,
        postal_code: str | None = None,
        start: dt.date | None = None,
        end: dt.date | None = None,
        province: str | None = None,
    ) -> int:
        data = {
            "street": street.strip() if street else None,
            "city": city.strip() if city else None,
            "country": country.strip() if country else None,
            "postal_code": postal_code.strip() if postal_code else None,
            "start": dt.date.fromisoformat(start) if isinstance(start, str) else start,
            "end": dt.date.fromisoformat(end) if isinstance(end, str) else end,
            "province": province.strip() if province else None,
        }

        updates = {key: value for key, value in data.items() if value is not None}
        if not updates:
            raise ValueError("No fields to update")

        with self.uow:
            return self.uow.address.update(key, **updates)

    def delete(
        self,
        key: int | None = None,
        street: str | None = None,
        city: str | None = None,
        country: str | None = None,
        postal_code: str | None = None,
        start: dt.date | None = None,
        end: dt.date | None = None,
        province: str | None = None,
    ) -> int:
        if key:
            with self.uow:
                return self.uow.address.delete(key=key)

        filters = {
            "street": street,
            "city": city,
            "country": country,
            "postal_code": postal_code,
            "start": start,
            "end": end,
            "province": province,
        }

        addresses = self.find(**filters)
        if not addresses:
            raise ValueError("No records found.")

        with self.uow:
            self.uow.address.delete(**filters)
            return len(addresses)

    def _overlaps(self, start: dt.date, end: dt.date) -> None:
        addresses = self.list()

        for address in addresses:
            existing_start = address.start
            existing_end = address.end or dt.date.today()

            if start < existing_end and existing_start < end:
                raise ValueError(
                    f"Period with start={start} and end={end} overlaps: {address}"
                )
        return
