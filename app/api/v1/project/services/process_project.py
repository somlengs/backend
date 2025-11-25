from uuid import UUID

from app.entities.schemas.auth_user import AuthUser


class ProcessProjectService:
    # Params
    project_id: UUID
    user: AuthUser

    # Data

    def __init__(self, project_id: UUID, user: AuthUser) -> None:
        self.project_id = project_id
        self.user = user
