import datetime as dt
import re
from typing import List, Optional
from folio.models import Travel
from folio.uow import UnitOfWork

COUNTRY_CODE_RE = re.compile(r"^[A-Z]{3}$")


class TravelService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, origin: str, destination: str, date: dt.date, notes: str = ""):
        date = dt.date.fromisoformat(date) if isinstance(date, str) else date

        origin, destination = origin.upper(), destination.upper()
        self._validate_country_codes(origin, destination)

        if self.find(origin, destination, date):
            raise ValueError(f"Travel already exists for {origin, destination, date}")

        travel = Travel(origin=origin, destination=destination, date=date, notes=notes)

        with self.uow:
            new_id = self.uow.travel.add(travel)
            return new_id

    def get(self, travel_id) -> Optional[Travel]:
        with self.uow:
            return self.uow.travel.get(travel_id)

    def list(self) -> List[Travel]:
        with self.uow:
            return self.uow.travel.list()

    def find(self, origin=None, destination=None, date=None) -> List[Travel]:
        date = dt.date.fromisoformat(date) if isinstance(date, str) else date
        with self.uow:
            return self.uow.travel.find(origin, destination, date)

    def _validate_country_codes(self, origin: str, destination: str) -> None:
        if not COUNTRY_CODE_RE.match(origin):
            raise ValueError(
                f"Invalid origin country code: '{origin}'. "
                f"Must be a valid 3-letter ISO 3166-1 alpha-3 code."
            )
        if not COUNTRY_CODE_RE.match(destination):
            raise ValueError(
                f"Invalid destination country code: '{destination}'. "
                f"Must be a valid 3-letter ISO 3166-1 alpha-3 code."
            )
