import logging
import sys

import uvicorn
from fastapi import FastAPI

from app.core.config import Config
from app.core.handlers.log_handlers.telegram import TelegramLogHandler
from app.core.logger import Logger


app = FastAPI()


@app.get('/')
async def root():
    Logger.get().debug('hi')
    return {'message': 'hi'}


def main():
    Logger.add_handler(TelegramLogHandler(level=logging.WARNING))

    try:
        uvicorn.run(
            app,
            port=Config.PORT,
            log_level=Config.LOG_LEVEL,
        )
    except KeyboardInterrupt:
        sys.exit(0)
