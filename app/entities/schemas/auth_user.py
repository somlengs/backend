from pydantic import BaseModel
from typing import Any, Optional


class AppMetadata(BaseModel):
    provider: Optional[str] = None


class AuthUser(BaseModel):
    id: str
    email: str | None = None
    role: str | None = None
    aud: str | None = None
    app_metadata: AppMetadata | None = None
    user_metadata: dict[str, Any] | None = None
    exp: int | None = None
    iat: int | None = None
