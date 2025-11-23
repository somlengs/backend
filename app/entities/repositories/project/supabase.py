from collections.abc import Callable
from datetime import UTC, datetime
from typing import override
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Config
from app.entities.models.project import ProjectTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.schemas.params.listing.project import ProjectListingParams
from app.entities.schemas.requests.project import UpdateProjectSchema
from app.entities.types.pagination import Paginated
from app.shared.utils.query import paginate_query

from .base import ProjectRepo


class SupabaseProjectRepo(ProjectRepo):
    def __init__(self) -> None:
        self.engine = create_engine(
            Config.Supabase.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3608,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

        super().__init__()

    @override
    def get_session(self) -> sessionmaker[Session]:
        return self.SessionLocal

    @override
    async def get_all_projects_for_user[T](
        self,
        db: Session,
        user_id: UUID | str,
        params: ProjectListingParams,
        *,
        mapper: Callable[[ProjectTable], T] = lambda x: x,
    ) -> Paginated[T]:
        name: str = params.project_name
        status: str | None = params.status
        limit = params.limit
        page = params.page
        sort = params.sort
        order = params.order

        query = db.query(ProjectTable).filter(ProjectTable.created_by == user_id)
        if len(name) > 2:
            query = query.filter(
                func.lower(ProjectTable.name).like(f"%{name.lower()}%")
            )

        if status is not None:
            query = query.filter(ProjectTable.status == status)

        sort_col = sort.column()
        query = order.apply(query, sort_col)

        return paginate_query(db, query, limit=limit, page=page, mapper=mapper)

    @override
    async def get_project_by_id(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> ProjectTable | None:
        return (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )

    @override
    async def create_project(
        self, db: Session, user_id: UUID | str, **kwargs
    ) -> ProjectTable:
        project = ProjectTable(created_by=user_id, **kwargs)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @override
    async def add_project(self, db: Session, project: ProjectTable) -> None:
        db.add(project)
        db.commit()
        db.refresh(project)

    @override
    async def update_project(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
        data: UpdateProjectSchema,
    ) -> ProjectTable | None:
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.id == project_id)
            .filter(ProjectTable.created_by == user_id)
            .one_or_none()
        )
        if project is None:
            return None

        data.update(project)

        db.commit()
        db.refresh(project)
        return project

    @override
    async def replace_project(
        self,
        db: Session,
        project: ProjectTable,
        user_id: UUID | str,
        exists_only: bool = False,
    ) -> ProjectTable:
        existing = await self.get_project_by_id(db, project.id, user_id)

        if existing is None:
            if exists_only:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    "Project not found",
                )
            db.add(project)
            db.commit()
            db.refresh(project)
            return project

        for column in ProjectTable.__table__.columns.keys():
            setattr(existing, column, getattr(project, column))
        existing.updated_at = datetime.now(UTC)

        db.commit()
        db.refresh(existing)
        return existing

    @override
    async def delete_project(
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
    ) -> bool:
        project = await self.get_project_by_id(db, project_id, user_id)

        if project is None:
            return False
        files_to_delete: list[str] = []
        for file in project.files:
            files_to_delete.append(file.file_path_raw)
            if file.file_path_cleaned:
                files_to_delete.append(file.file_path_cleaned)

        await SSSRepo.instance.bulk_delete(files_to_delete)

        db.delete(project)
        db.commit()
        return True
