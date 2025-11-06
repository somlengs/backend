from __future__ import annotations

from enum import StrEnum
from typing import Literal
from collections.abc import Callable

from sqlalchemy import asc, desc, Column
from sqlalchemy.orm import Query

class Ordering(StrEnum):
    asc = 'asc'
    desc = 'desc'
    
    def apply[T](self, query: Query[T], column: Column[T]) -> Query[T]:
        if self == Ordering.desc:
            return query.order_by(desc(column))
        return query.order_by(asc(column))
