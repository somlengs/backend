import os
from collections.abc import Callable
from typing import Literal, cast


def require_env[T](key: str, t: type[T] | Callable[[str], T] = str) -> T:
    value = os.getenv(key)
    if value is None or value.strip() == '':
        raise EnvironmentError(f'Missing required environment variable: {key}')
    return t(value)


def optional_env[T](key: str, default: T) -> T:
    value = os.getenv(key)
    if value is None or value.strip() == '':
        return default

    cls = type(default)
    return cls(value)
