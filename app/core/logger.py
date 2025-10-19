import logging
from logging import Handler
from logging import Logger as L
from collections.abc import Sequence

from app.core.config import Config
from app.entities.types import LogLevelT

class Logger:

    @classmethod
    def get(cls) -> L:
        return logging.getLogger('uvicorn.error')
        
    @classmethod
    def add_handler(
        cls,
        handler: Handler
        ) -> None:
        cls.get().addHandler(handler)
