from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Column, asc, desc
from sqlalchemy.orm import Query


class Ordering(StrEnum):
    asc = "asc"
    desc = "desc"

    def apply[T](self, query: Query[T], column: Column[T]) -> Query[T]:
        if self == Ordering.desc:
            return query.order_by(desc(column))
        return query.order_by(asc(column))
