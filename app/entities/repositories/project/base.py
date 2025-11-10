from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from collections.abc import Callable, Generator
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from app.entities.models.project import ProjectTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable
from app.entities.schemas.params.listing.project import ProjectListingParams
from app.entities.schemas.requests.project import UpdateProjectSchema
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
    async def get_all_projects_for_user[T](
        self,
        db: Session,
        user_id: UUID | str,
        params: ProjectListingParams,
        *,
        mapper: Callable[[ProjectTable], T] = lambda x: x,
    ) -> Paginated[T]:
        ...

    @abstractmethod
    async def get_project_by_id(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> ProjectTable | None:
        ...
        
    async def get_project_or_404(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> ProjectTable:
        project = await self.get_project_by_id(
            db,
            project_id,
            user_id,
        )

        if project is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                'Project not found',
            )
            
        return project

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
        data: UpdateProjectSchema,
    ) -> ProjectTable | None:
        ...

    @abstractmethod
    async def replace_project(
        self,
        db: Session,
        project: ProjectTable,
        user_id: UUID | str,
        exists_only: bool = False,
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
