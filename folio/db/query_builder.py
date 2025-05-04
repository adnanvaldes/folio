from typing import TypeVar, Generic, Type, Any
from sqlmodel import SQLModel, Session, select, func, and_, or_, col


T = TypeVar("T", bound=SQLModel)


class QueryBuilder(Generic[T]):
    """Generic class to build SQLModel queries"""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
        self.query: select = select(model)
        self.filters_applied = 0

    def text_filter(self, field, value: list[str] | None, partial: bool = True):
        if value:
            value = [v.lower() for v in value]
            if partial:
                conditions = [col(field).ilike(f"%{v}%") for v in value if v]
                self.query = self.query.where(or_(*conditions))
            else:
                self.query = self.query.where(func.lower(col(field)).in_(value))
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
        exact_value: list[int] | None = None,
    ):
        if exact_value is not None:
            self.query = self.query.where(col(field).in_(exact_value))
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
