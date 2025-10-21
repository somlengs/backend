import logging
from logging import Handler
from logging import Logger
from collections.abc import Sequence

from app.core.config import Config
from app.entities.types import LogLevelT


def get() -> Logger:
    return logging.getLogger('uvicorn.error')

def add_handler(handler: Handler) -> None:
    get().addHandler(handler)
