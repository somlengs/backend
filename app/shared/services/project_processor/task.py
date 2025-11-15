from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any, TYPE_CHECKING
from contextlib import suppress
import time
from uuid import UUID

from app.core.logger import get
from app.entities.models.project import ProjectTable
from app.entities.repositories.project.base import ProjectRepo
from app.shared.services.project_processor.sub_task import SubTask
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.task_log import SubTaskLog, TaskLog

if TYPE_CHECKING:
    from . import ProjectProcessor
    from .sub_task import SubTask


logger = get()


class ProcessingTask:
    project: ProjectTable
    sub_tasks: dict[SubTask, ProcessingStatus]
    logs: list[TaskLog]

    _listeners: list[asyncio.Queue[TaskLog]]
    _manager: type[ProjectProcessor]
    
    @property
    def id(self) -> UUID:
        return self.project.id

    def __init__(self, manager: type[ProjectProcessor], project: ProjectTable) -> None:
        self.project = project
        self.sub_tasks = {}
        self.logs = []
        self._listeners = []
        self._manager = manager

    def subscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        self._listeners.append(queue)

    def unsubscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        with suppress(ValueError):
            self._listeners.remove(queue)

    async def _notify_listeners(
        self,
        message: str | None = None,
        error: int | None = None,
        stop_connections: bool = False,
    ) -> None:
        queues = self._listeners.copy()
        
        tasks_len = len(self.sub_tasks)
        completed_len = 0
        task_statuses = {}
        for t, s in self.sub_tasks.items():
            if s == ProcessingStatus.completed:
                completed_len += 1
            task_statuses[t.id] = s

        log = TaskLog(
            project_id=self.project.id,
            status=self.project.status,
            completed_tasks=completed_len,
            total_tasks=tasks_len,
            message=message or '',
            error=error,
            task_statuses=task_statuses,
            stop_connections=stop_connections,
        )

        for q in queues:
            await q.put(log)
            
    async def _on_sub_task_update(self, log: SubTaskLog, task: SubTask) -> None:
        self.sub_tasks[task] = log.status
        await self._notify_listeners(log.message, error=log.error)

    async def _run_task(self, task: SubTask) -> SubTask:
        t0 = time.perf_counter()
        await task.start()
        logger.debug(f'Transcription for file {task.id} finished (took {(time.perf_counter() - t0):.4f}s)')
        return task

    async def start(self) -> None:
        if self.project.status != ProcessingStatus.pending:
            msg = f'Cannot start non-pending project {self.project.id}. (current {self.project.status})'
            # logger.error(msg)
            raise RuntimeError(msg)

        t0 = time.perf_counter()
        logger.info(f'Processing started for project {self.project.id}')

        files = self.project.files

        db = ProjectRepo.instance.get_session()()
        self.project.status = ProcessingStatus.processing
        await ProjectRepo.instance.replace_project(db, self.project, self.project.created_by)

        for file in files:
            t = SubTask(db, file)
            t.listener = self._on_sub_task_update
            self.sub_tasks[t] = file.transcription_status
        tasks: list[Coroutine[Any, Any, SubTask]] = []

        for t, s in self.sub_tasks.items():
            if s == ProcessingStatus.pending:
                tasks.append(self._run_task(t))

        results = await asyncio.gather(*tasks)
        self.project.status = ProcessingStatus.completed
        for r in results:
            r.commit()
            
        await ProjectRepo.instance.replace_project(db, self.project, self.project.created_by)
        
        self._manager.on_task_complete(self.id)
        await self._notify_listeners('Finished', stop_connections=True)
        logger.info(f'Transcription finished for project {self.id} (took {(time.perf_counter() - t0):.4f}s)')
