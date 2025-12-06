import asyncio
import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import load_routers
from app.core import logger
from app.core.config import Config
from app.core.handlers.log_handlers.telegram import TelegramLogHandler
from app.core.lifespan import lifespan
from app.core.middlewares.logger import ExceptionLoggingMiddleware
from app.shared.services.metadata_exporter import CSVExporter, add_exporter

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API routers
load_routers(app)


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
    app.add_middleware(ExceptionLoggingMiddleware)
    logger.add_handler(TelegramLogHandler(level=logging.WARNING))

    add_exporter('csv', 'Wav2Vec2', CSVExporter(','))
    add_exporter('tsv', 'Wav2Vec2', CSVExporter('\t'))

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)
