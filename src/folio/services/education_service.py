from folio.models import Education
from folio.uow import UnitOfWork


class EducationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def add(self, education: Education) -> None:
        with self.uow:
            self.uow.education.add(education)

    def remove(self, education: Education) -> None:
        with self.uow:
            self.uow.education.remove(education)

    def replace(self, old: Education, new: Education) -> None:
        with self.uow:
            self.uow.education.replace(old, new)

    def find(self, **filters) -> list[Education]:
        with self.uow:
            return self.uow.education.find(**filters)

    def list_all(self) -> list[Education]:
        with self.uow:
            return self.uow.education.list_all()
