import asyncio
from math import ceil
import os
from collections.abc import Callable
from pathlib import Path
import time
import re

from app.entities.types.pagination import Paginated
from app.core.logger import get as get_logger

logger = get_logger()

def require_env[T](key: str, t: type[T] | Callable[[str], T] = str) -> T:
    value = os.getenv(key)
    if value is None or value.strip() == '':
        raise EnvironmentError(f'Missing required environment variable: {key}')
    return t(value) # type: ignore


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
    return cls(value) # type: ignore


def paginate[T](data: list[T], skip: int = 0, limit: int = 100) -> Paginated[T]:

    total_items = len(data)
    total_pages = ceil(total_items / limit) if limit else 1
    current_page = (skip // limit) + 1 if limit else 1

    paginated = data[skip:skip + limit]
    return {
        'data': paginated,
        'pagination': {
            'limit': limit,
            'page': current_page,
            'total_pages': total_pages,
            'total_items': total_items,
        }
    }


async def convert_to_wav(path: Path) -> Path:
        if path.name.endswith('.wav'):
            logger.debug('Already a wav file, ignored.')
            return path
        
        output_path = path.with_suffix('wav')
        t0 = time.perf_counter()
        
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', '-i', str(path), str(output_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.warning(stderr.decode())
            raise RuntimeError(f'Failed to convert {path}')
        
        logger.info(f'Converted "{path.name}" to "{output_path.name}" ({(time.perf_counter() - t0):.4f}s)')
        return output_path

def bump_name(name: str, step: int = 1) -> str:
    m = re.search(r"(\d+)$", name)
    if not m:
        return f"{name}_1"
    num = m.group(1)
    new = int(num) + step
    width = len(num)
    return f"{name[:m.start()]}{str(new).zfill(width)}"
