from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Generator
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from app.entities.models.project import ProjectTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable
from app.entities.schemas.params.listing.project import ProjectListingParams
from app.entities.types.pagination import Paginated


class ProjectRepo(ABC):

    instance: ProjectRepo

    @classmethod
    def init(cls, repo: ProjectRepo) -> None:
        cls.instance = repo

    @abstractmethod
    def get_session(self) -> sessionmaker[Session]:
        ...

    @abstractmethod
    async def get_all_projects_for_user(
        self,
        db: Session,
        user_id: UUID | str,
        params: ProjectListingParams
    ) -> Paginated[ProjectTable]:
        ...

    @abstractmethod
    async def get_project_by_id(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> ProjectTable | None:
        ...

    @abstractmethod
    async def create_project(self, db: Session, user_id: UUID | str, **kwargs) -> ProjectTable:
        ...

    @abstractmethod
    async def add_project(self, db: Session, project: ProjectTable) -> None:
        ...

    @abstractmethod
    async def update_project(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
        **kwargs,
    ) -> ProjectTable | None:
        ...

    @abstractmethod
    async def replace_project(
        self,
        db: Session,
        project: ProjectTable,
        user_id: UUID | str,
    ) -> ProjectTable:
        ...

    @abstractmethod
    async def delete_project(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> bool:
        ...
