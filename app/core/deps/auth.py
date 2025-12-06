from typing import Optional
from fastapi import HTTPException, Request, status, Query
import jwt

from app.core.config import Config
from app.core.logger import get
from app.entities.schemas.auth_user import AuthUser

logger = get()

def auth_user(request: Request) -> AuthUser:
    auth = request.headers.get('Authorization')

    if not auth or not auth.startswith('Bearer '):
        logger.warning('Auth failed: missing or malformed Authorization header')
        raise HTTPException(401, 'Invalid token payload')

    token = auth.removeprefix('Bearer ').strip()

    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated',
        )
    except jwt.PyJWTError as e:
        logger.warning(f'Auth failed: token decode error ({e.args[0]})')
        raise HTTPException(401, 'Invalid auth token')

    sub = payload.get('sub')
    if not sub:
        logger.warning('Auth failed: token missing subject (sub)')
        raise HTTPException(401, 'Invalid token payload')

    return AuthUser(
        id=sub,
        email=payload.get('email'),
        role=payload.get('role'),
        aud=payload.get('aud'),
        app_metadata=payload.get('app_metadata'),
        user_metadata=payload.get('user_metadata'),
        exp=payload.get('exp'),
        iat=payload.get('iat'),
    )


def auth_user_sse(
    request: Request,
    token: Optional[str] = Query(None, description="JWT token for SSE authentication")
) -> AuthUser:
    """
    Auth dependency for SSE endpoints that accepts token from query params.
    EventSource doesn't support custom headers, so we need to pass token via URL.
    """
    # Try to get token from query param first (for SSE)
    if not token:
        # Fallback to Authorization header
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            logger.warning('SSE Auth failed: missing token in query param or Authorization header')
            raise HTTPException(401, 'Invalid token payload')
        token = auth.removeprefix('Bearer ').strip()

    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated',
        )
    except jwt.PyJWTError as e:
        logger.warning(f'SSE Auth failed: token decode error ({e.args[0]})')
        raise HTTPException(401, 'Invalid auth token')

    sub = payload.get('sub')
    if not sub:
        logger.warning('SSE Auth failed: token missing subject (sub)')
        raise HTTPException(401, 'Invalid token payload')

    return AuthUser(
        id=sub,
        email=payload.get('email'),
        role=payload.get('role'),
        aud=payload.get('aud'),
        app_metadata=payload.get('app_metadata'),
        user_metadata=payload.get('user_metadata'),
        exp=payload.get('exp'),
        iat=payload.get('iat'),
    )
