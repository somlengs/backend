import httpx
import fastapi as api

from app.core.config import Config
from app.entities.schemas.requests.login import LoginRequest
from app.core.logger import get

router = api.APIRouter(prefix='/dev')

logger = get()

@router.post('/login')
async def login(body: LoginRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f'{Config.Supabase.URL}/auth/v1/token?grant_type=password',
            json={"email": body.email, "password": body.password},
            headers={
                "apikey": Config.Supabase.ANON_KEY,
                "Content-Type": "application/json",
            },
        )

    data = resp.json()

    if resp.status_code != 200:
        data['message'] = data['msg']
        del data['msg']
        logger.warning(data['message'])
        raise api.HTTPException(status_code=data.status_code, detail=data)

    return {
        "access_token": data.get("access_token"),
        "user": data.get("user"),
    }
