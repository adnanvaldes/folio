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

    def exact_match(self, field, value: str | None):
        if value:
            self.query = self.query.where(col(field) == value)
            self.filters_applied += 1
        return self

    def range(
        self,
        field,
        min_value: int | None = None,
        max_value: int | None = None,
        exact_value: int | None = None,
    ):
        if exact_value is not None:
            self.query = self.query.where(col(field) == exact_value)
            print(self.query)
            self.filters_applied += 1

        elif min_value and max_value:
            # Use inclusive values
            self.query = self.query.where(
                and_(col(field) >= min_value, col(field) <= max_value)
            )
            print(self.query)
            self.filters_applied += 1
        elif min_value:
            self.query = self.query.where(col(field) >= min_value)
            self.filters_applied += 1
        elif max_value:
            self.query = self.query.where(col(field) <= max_value)
            self.filters_applied += 1
        return self

    def reset(self):
        self.query = select(self.model)
        self.filters_applied = 0
        return self

    def get_results(self, limit: int | None = None):
        if limit:
            self.query = self.query.limit(limit)
        return self.session.exec(self.query).all()
