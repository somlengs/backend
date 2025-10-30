from collections.abc import Generator
from typing import override
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import NoResultFound

from app.core.config import Config
from app.entities.models.project import ProjectTable
from .base import ProjectRepo


class SupabaseProjectRepo(ProjectRepo):

    def __init__(self) -> None:
        self.engine = create_engine(Config.Supabase.DATABASE_URL)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

        super().__init__()

    @override
    def get_session(self) -> sessionmaker[Session]:
        return self.SessionLocal

    @override
    async def get_all_projects_for_user(
        self, db: Session, user_id: UUID | str, **kwargs
    ) -> list[ProjectTable]:
        query = db.query(ProjectTable).filter(ProjectTable.created_by == user_id)
        for key, value in kwargs.items():
            if value is None:
                continue
            if hasattr(ProjectTable, key):
                query = query.filter(getattr(ProjectTable, key) == value)

        return query.all()

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
        **kwargs,
    ) -> ProjectTable | None:
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )
        if project is None:
            return None

        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)

        db.commit()
        db.refresh(project)
        return project

    @override
    async def replace_project(
        self,
        db: Session,
        project: ProjectTable,
        user_id: UUID | str,
    ) -> ProjectTable:
        existing = (
            db.query(ProjectTable)
            .filter(ProjectTable.id == project.id)
            .one_or_none()
        )

        if existing is None:
            db.add(project)
            db.commit()
            db.refresh(project)
            return project

        for column in ProjectTable.__table__.columns.keys():
            setattr(existing, column, getattr(project, column))

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
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )
        if project is None:
            return False

        db.delete(project)
        db.commit()
        return True
