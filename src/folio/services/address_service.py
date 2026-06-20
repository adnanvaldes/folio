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

        with self.uow:
            if self.uow.address.find(**data):
                fields = ", ".join(f"{v}" for _, v in data.items())
                raise ValueError(f"Address already already exists for {fields}")

            if data["end"] is None:
                for existing in self.uow.address.find_open():
                    if existing.start < data["start"]:
                        new_end = data["start"] - dt.timedelta(days=1)
                        self.uow.address.update(
                            filters={
                                "street": existing.street,
                                "city": existing.city,
                                "country": existing.country,
                                "postal_code": existing.postal_code,
                                "province": existing.province,
                                "start": existing.start,
                                "end": None,
                            },
                            end=new_end,
                        )
                    else:
                        raise ValueError(
                            f"Cannot open address starting {data['start']}: "
                            f"an address is already open starting {existing.start}: {existing}"
                        )

            self._overlaps(data["start"], data["end"], self.uow)
            return self.uow.address.add(Address(**data))

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

    def update(self, match: dict, updates: dict) -> int:
        updates = {
            "street": updates["street"].strip() if updates.get("street") else None,
            "city": updates["city"].strip() if updates.get("city") else None,
            "country": updates["country"].strip() if updates.get("country") else None,
            "postal_code": (
                updates["postal_code"].strip() if updates.get("postal_code") else None
            ),
            "start": (
                dt.date.fromisoformat(updates["start"])
                if isinstance(updates.get("start"), str)
                else updates.get("start")
            ),
            "end": (
                dt.date.fromisoformat(updates["end"])
                if isinstance(updates.get("end"), str)
                else updates.get("end")
            ),
            "province": (
                updates["province"].strip() if updates.get("province") else None
            ),
        }

        data = {k: v for k, v in updates.items() if v is not None}
        if not data:
            raise ValueError("No fields to update")

        with self.uow:
            records = self.uow.address.find(**match)
            if not records:
                raise ValueError(f"No address found matching {match}")
            if len(records) > 1:
                raise ValueError(f"Multiple addresses found matching {match}")
            return self.uow.address.update(records[0], **data)

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

    def _overlaps(self, start: dt.date, end: dt.date, uow: UnitOfWork) -> None:
        effective_end = end or dt.date.today()
        addresses = uow.address.list()

        for address in addresses:
            existing_start = address.start
            existing_end = address.end or dt.date.today()

            if start < existing_end and existing_start < effective_end:
                raise ValueError(
                    f"Period with start={start} and end={end} overlaps: {address}"
                )
        return
