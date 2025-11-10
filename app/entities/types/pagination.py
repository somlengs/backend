from typing import TypedDict


class PaginationMeta(TypedDict):
    page: int
    limit: int
    total_pages: int
    total_items: int


class Paginated[T](TypedDict):
    data: list[T]
    pagination: PaginationMeta
