from collections.abc import Callable
from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session, Query

from app.entities.types.pagination import Paginated, PaginationMeta


def paginate_query[T, R](
    db: Session,
    query: Query[T],
    limit: int = 20,
    page: int = 1,
    *,
    mapper: Callable[[T], R] = lambda x: x,
) -> Paginated[R]:
    total_items: int = db.query(func.count()).select_from(
        query.subquery()).scalar() or 0
    offset = (page - 1) * limit
    total_page: int = ceil(total_items / limit) if total_items else 1

    data: list[T] = query.offset(offset).limit(limit).all()

    pagination_meta: PaginationMeta = {
        'limit': limit,
        'page': page,
        'total_pages': total_page,
        'total_items': total_items,
    }

    return {
        'data': list(map(mapper, data)),
        'pagination': pagination_meta
    }
