from typing import override

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.entities.models.project import ProjectTable
from .base import ProjectRepo


class SupabaseProjectRepo(ProjectRepo):

    def __init__(self) -> None:
        super().__init__()

    @override
    async def get_all_projects_for_user(
        self,
        db: Session,
        user_id: str,
        **kwargs
    ) -> list[ProjectTable]:
        query = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
        )
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
        project_id: str,
        user_id: str,
    ) -> ProjectTable | None:
        return (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )

    @override
    async def create_project(self, db: Session, user_id: str, **kwargs) -> ProjectTable:
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
    async def update_project(self, db: Session, project_id: str, user_id: str, **kwargs) -> ProjectTable:
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )
        if project is None:
            raise NoResultFound("Project not found or not owned by user")

        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)

        db.commit()
        db.refresh(project)
        return project

    @override
    async def delete_project(self, db: Session, project_id: str, user_id: str) -> None:
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )
        if project is None:
            raise NoResultFound("Project not found or not owned by user")

        db.delete(project)
        db.commit()
