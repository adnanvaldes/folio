from typing import TypeVar, Generic, Optional, Type
from sqlmodel import SQLModel, Session, select, func


T = TypeVar("T", bound=SQLModel)


class QueryBuilder(Generic[T]):
    """Generic class to build SQLModel queries"""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
        self.query: select = select(model)
        self.filters_applied = 0

    def text_filter(self, field, value: Optional[str], exact_match: bool = True):
        if value:
            if exact_match:
                self.query = self.query.where(func.lower(field) == value.lower())
            else:
                self.query = self.query.where(field.ilike(f"%{value.lower()}%"))
            self.filters_applied += 1
        return self

    def get_results(self, limit: Optional[int] = None):
        if limit:
            self.query = self.query.limit(limit)
        return self.session.exec(self.query).all()
