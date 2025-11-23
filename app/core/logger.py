import logging
from logging import Handler, Logger


def get() -> Logger:
    return logging.getLogger('uvicorn')

def add_handler(handler: Handler) -> None:
    get().addHandler(handler)
