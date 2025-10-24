from fastapi import HTTPException, Request, status
import jwt

from app.core.config import Config
from app.entities.schemas.auth_user import AuthUser


def auth_user(request: Request) -> AuthUser:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )
    token = auth_header.removeprefix('Bearer ').strip()
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated'
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {e}'
        )
    if 'sub' not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )

    return AuthUser(
        id=payload['sub'],
        email=payload.get('email'),
        role=payload.get('role'),
        aud=payload.get('aud'),
        app_metadata=payload.get('app_metadata'),
        user_metadata=payload.get('user_metadata'),
        exp=payload.get('exp'),
        iat=payload.get('iat'),
    )
