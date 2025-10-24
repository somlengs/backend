from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.entities.types.pagination import Paginated
from app.entities.models.project import ProjectTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable


class ProjectRepo(ABC):

    instance: ProjectRepo

    @classmethod
    def init(cls, repo: ProjectRepo) -> None:
        cls.instance = repo

    @abstractmethod
    async def get_all_projects_for_user(
        self,
        db: Session,
        user_id: str,
        **kwargs
    ) -> list[ProjectTable]:
        ...

    @abstractmethod
    async def get_project_by_id(
        self,
        db: Session,
        project_id: str,
        user_id: str,
    ) -> ProjectTable | None:
        ...

    @abstractmethod
    async def create_project(self, db: Session, user_id: str, **kwargs) -> ProjectTable:
        ...

    @abstractmethod
    async def add_project(self, db: Session, project: ProjectTable) -> None:
        ...

    @abstractmethod
    async def update_project(self, db: Session, project_id: str, user_id: str, **kwargs) -> ProjectTable:
        ...

    @abstractmethod
    async def delete_project(self, db: Session, project_id: str, user_id: str) -> None:
        ...
