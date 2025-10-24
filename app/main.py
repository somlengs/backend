import asyncio
import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import load_routers
from app.core.config import Config
from app.core.handlers.log_handlers.telegram import TelegramLogHandler
from app.core import logger
from app.core.lifespan import lifespan
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.project.supabase import SupabaseProjectRepo


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {'message': 'hi'}


def setup_server() -> uvicorn.Server:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    load_routers(app)
    return server


def main():
    server = setup_server()
    # logger.add_handler(TelegramLogHandler(level=logging.WARNING))

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)
