from math import ceil
import os
from collections.abc import Callable, Iterable
from typing import Literal, cast

from app.entities.types.pagination import Paginated


def require_env[T](key: str, t: type[T] | Callable[[str], T] = str) -> T:
    value = os.getenv(key)
    if value is None or value.strip() == '':
        raise EnvironmentError(f'Missing required environment variable: {key}')
    return t(value)


def parse_list[T](csv: str, t: type[T] | Callable[[str], T] = str) -> list[T]:
    parts = []

    for value in csv.split(','):
        part = value.strip()

        if part:
            parts.append(part)

    return parts


def optional_env[T](key: str, default: T) -> T:
    value = os.getenv(key)
    if value is None or value.strip() == '':
        return default

    cls = type(default)
    return cls(value)


def paginate[T](data: list[T], skip: int = 0, limit: int = 100) -> Paginated[T]:

    total_items = len(data)
    total_pages = ceil(total_items / limit) if limit else 1
    current_page = (skip // limit) + 1 if limit else 1

    paginated = data[skip:skip + limit]
    return {
        "data": paginated,
        "pagination": {
            "limit": limit,
            "page": current_page,
            "total_page": total_pages,
        }
    }
