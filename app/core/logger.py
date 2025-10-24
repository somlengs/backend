import logging
from logging import Handler
from logging import Logger


def get() -> Logger:
    return logging.getLogger('uvicorn.error')

def add_handler(handler: Handler) -> None:
    get().addHandler(handler)
