import time

import httpx
import fastapi as api

from app.core.config import Config
from app.entities.schemas.requests.login import LoginRequest
from app.core.logger import get

router = api.APIRouter(prefix='/dev')
logger = get()


@router.post('/login')
async def login(body: LoginRequest):
    t0 = time.perf_counter()
    if Config.ENVIRONMENT != 'DEV':
        logger.warning('Login called outside DEV')
        raise api.HTTPException(api.status.HTTP_403_FORBIDDEN, 'Not allowed')
    logger.debug(f'email={body.email}, password_len={len(body.password or '')}')

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f'{Config.Supabase.URL}/auth/v1/token?grant_type=password',
                json={'email': body.email, 'password': body.password},
                headers={
                    'apikey': Config.Supabase.ANON_KEY,
                    'Content-Type': 'application/json',
                },
            )
        except Exception:
            logger.error('Supabase request failed', exc_info=True)
            raise api.HTTPException(500, 'Auth provider unreachable')

    elapsed = time.perf_counter() - t0
    logger.debug(f'Supabase responded {resp.status_code} in {elapsed:.3f}s')

    try:
        data = resp.json()
    except Exception:
        logger.error('Supabase returned invalid JSON', exc_info=True)
        raise api.HTTPException(502, 'Bad auth response')

    if resp.status_code != 200:
        msg = data.get('msg') or data.get('message') or 'Login failed'
        logger.warning(f'Login failed for {body.email}: {msg}')
        raise api.HTTPException(resp.status_code, msg)

    logger.debug(f'Login success for {body.email} ({elapsed:.3f}s)')
    return {
        'access_token': data.get('access_token'),
        'user': data.get('user'),
    }
