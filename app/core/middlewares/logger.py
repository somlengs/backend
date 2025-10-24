from logging import Logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core import logger

_logger = logger.get()

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):


    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            _logger.exception("Unhandled exception during request: %s %s", request.method, request.url)
            raise
