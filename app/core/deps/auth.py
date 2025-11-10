from fastapi import HTTPException, Request, status
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
