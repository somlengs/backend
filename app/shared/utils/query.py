from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session, Query

from app.entities.types.pagination import Paginated, PaginationMeta


def paginate_query[T](
    db: Session,
    query: Query[T],
    limit: int = 20,
    offset: int = 0,
) -> Paginated[T]:
    total_items: int = db.query(func.count()).select_from(
        query.subquery()).scalar() or 0
    page: int = (offset // limit) + 1
    total_page: int = ceil(total_items / limit) if total_items else 1

    data: list[T] = query.offset(offset).limit(limit).all()

    pagination_meta: PaginationMeta = {
        'limit': limit,
        'page': page,
        'total_page': total_page,
        'total_items': total_items,
    }

    return {
        'data': data,
        'pagination': pagination_meta
    }
