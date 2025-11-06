from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from app.entities.models.project import ProjectTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.internals.task import ProcessingTask
from app.entities.types.enums.processing_status import ProcessingStatus


class ProjectProcessor:
    instance: ProjectProcessor
    tasks: dict[UUID, ProcessingTask]

    def __init__(self) -> None:
        self.tasks: dict[UUID, ProcessingTask] = {}

    @classmethod
    def init(cls):
        cls.instance = cls()

    async def process_task(
        self,
        project: ProjectTable,
        db: Session,
    ):
        if project.status != ProcessingStatus.draft:
            raise HTTPException(
                status_code=400, detail='Project already started')

        task = ProcessingTask(project)

    @staticmethod
    async def update_db(db: Session, task: ProcessingTask, user_id: UUID):
        await ProjectRepo.instance.replace_project(db, task.project, user_id)
