import asyncio
import logging
import sys

import uvicorn
from fastapi import FastAPI

from app.core.config import Config
from app.core.handlers.log_handlers.telegram import TelegramLogHandler
from app.core import logger


app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'hi'}


def setup_server() -> uvicorn.Server:
    config = uvicorn.Config(
        app,
        port=Config.PORT,
        log_level=Config.LOG_LEVEL
    )
    server = uvicorn.Server(config)
    server.config.configure_logging()
    loop_factory = config.get_loop_factory()

    if loop_factory:
        asyncio.set_event_loop(loop_factory())

    return server


def main():
    server = setup_server()

    logger.add_handler(TelegramLogHandler(level=logging.WARNING))

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)
