from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator, Callable
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from app.entities.models.project import ProjectTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.types.task_log import TaskLog
from app.shared.services.project_processor.task import ProcessingTask
from app.entities.types.enums.processing_status import ProcessingStatus


class ProjectProcessor:
    tasks: dict[UUID, ProcessingTask] = {}

    @classmethod
    def start(
        cls,
        project: ProjectTable,
    ):
        if project.status == ProcessingStatus.loading:
            raise HTTPException(
                status_code=400, detail='Project is loading',
            )
        if project.status != ProcessingStatus.pending:
            raise HTTPException(
                status_code=400, detail='Project is already processing',
            )

        task = ProcessingTask(cls, project)
        cls.tasks[project.id] = task
        
        asyncio.create_task(task.start())

    @classmethod
    def on_task_complete(cls, project_id: UUID) -> None:
        cls.tasks.pop(project_id, None)  # Use pop to avoid KeyError if already removed

    @classmethod
    def get_stream(cls, project_id: UUID) -> Callable[[], AsyncGenerator[Any, str]]:
        task = cls.tasks.get(project_id)
        if task is None:
            raise HTTPException(
                404, f'No running tasks for project {project_id}',
            )

        queue = asyncio.Queue[TaskLog]()
        task.subscribe(queue)
        last_log: TaskLog | None = None

        async def generator():
            while True:
                log = await queue.get()
                yield cls.log_to_json_str(log)
                if log.stop_connections:
                    return

        return generator

    @classmethod
    def restart(cls) -> None:
        ...

    @classmethod
    def exit(cls) -> None:
        ...

    @staticmethod
    async def update_db(db: Session, task: ProcessingTask, user_id: UUID):
        await ProjectRepo.instance.replace_project(db, task.project, user_id)

    @staticmethod
    def log_to_json_str(log: TaskLog) -> str:
        data = {
            'project_id': str(log.project_id),
            'status': log.status,
            'completed_tasks': log.completed_tasks,
            'total_tasks': log.total_tasks,
            'message': log.message,
            'error': log.error,
            'task_statuses':log.task_statuses
        }
        
        str_data = json.dumps(data, ensure_ascii=False)
        return f'data: {str_data}\n\n'
