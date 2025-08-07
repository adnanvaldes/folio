import datetime as dt
from typing import List, Optional
from folio.models import Employment
from folio.uow import UnitOfWork


class EmploymentService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(
        self,
        company: str,
        supervisor: str,
        address: str,
        phone: str,
        start: dt.date,
        end: dt.date | None = None,
    ) -> int:

        start = dt.date.fromisoformat(start) if isinstance(start, str) else start
        end = dt.date.fromisoformat(end) if isinstance(end, str) else end

        if self.find(company=company, start=start):
            raise ValueError(f"Employment already exists for {company, start}")

        employment = Employment(
            start=start,
            end=end,
            company=company,
            supervisor=supervisor,
            address=address,
            phone=phone,
        )

        with self.uow:
            new_id = self.uow.employment.add(employment)
            return new_id

    def get(self, employment_id: int) -> Optional[Employment]:
        with self.uow:
            return self.uow.employment.get(employment_id)

    def list(self) -> List[Employment]:
        with self.uow:
            return self.uow.employment.list()

    def find(
        self,
        start: dt.date = None,
        end: dt.date = None,
        company: str = None,
        supervisor: str = None,
        address: str = None,
        phone: str = None,
    ) -> List[Employment]:
        data = {
            "start": dt.date.fromisoformat(start) if isinstance(start, str) else start,
            "end": dt.date.fromisoformat(end) if isinstance(end, str) else end,
            "company": company.strip() if company else None,
            "supervisor": supervisor.strip() if supervisor else None,
            "address": address.strip() if address else None,
            "phone": phone.strip() if phone else None,
        }

        with self.uow:
            return self.uow.employment.find(**data)
