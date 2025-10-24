import httpx
import fastapi as api

from app.core.config import Config
from app.entities.schemas.requests.login import LoginRequest

router = api.APIRouter(prefix='/dev')


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


    if resp.status_code != 200:
        raise api.HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    return {
        "access_token": data.get("access_token"),
        "user": data.get("user"),
    }
