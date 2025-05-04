from typing import TypeVar, Generic, Type
from sqlmodel import SQLModel, Session, select, func, and_, col


T = TypeVar("T", bound=SQLModel)


class QueryBuilder(Generic[T]):
    """Generic class to build SQLModel queries"""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
        self.query: select = select(model)
        self.filters_applied = 0

    def text_filter(self, field, value: str | None, partial: bool = True):
        if value:
            if partial:
                self.query = self.query.where(col(field).ilike(f"%{value.lower()}%"))
            else:
                self.query = self.query.where(func.lower(col(field)) == value.lower())
            self.filters_applied += 1
        return self

    def exact_match(self, field, value: Any = None):
        if value is not None:
            self.query = self.query.where(col(field) == value)
            self.filters_applied += 1
        return self

    def boolean_filter(self, field, value: bool | None = None):
        return self.exact_match(field=field, value=value)

    def range_filter(
        self,
        field,
        min_value: int | None = None,
        max_value: int | None = None,
        exact_value: int | None = None,
    ):
        if exact_value is not None:
            self.query = self.query.where(col(field) == exact_value)
            self.filters_applied += 1
        else:
            conditions = []
            if min_value is not None:
                conditions.append(col(field) >= min_value)
            if max_value is not None:
                conditions.append(col(field) <= max_value)

            if conditions:
                self.query = self.query.where(and_(*conditions))
                self.filters_applied += 1
        return self

    def reset(self):
        self.query = select(self.model)
        self.filters_applied = 0
        return self

    def run(self, limit: int | None = None):
        if limit:
            self.query = self.query.limit(limit)
        return self.session.exec(self.query).all()
