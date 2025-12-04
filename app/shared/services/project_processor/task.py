from __future__ import annotations

import asyncio
import time
from collections.abc import Coroutine
from contextlib import suppress
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.core.config import Config
from app.core.logger import get
from app.entities.models.project import ProjectTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.events.project_event import ProjectEvent
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.task_log import ChangedFileStatusT, SubTaskLog, TaskLog
from app.shared.services.event_manager import EventManager
from app.shared.services.project_processor.sub_task import SubTask

if TYPE_CHECKING:
    from . import ProjectProcessor
    from .sub_task import SubTask


logger = get()


class ProcessingTask:
    project: ProjectTable
    sub_tasks: dict[SubTask, ProcessingStatus]
    changes: list[ChangedFileStatusT]

    _listeners: list[asyncio.Queue[TaskLog]]
    _manager: type[ProjectProcessor]

    @property
    def id(self) -> UUID:
        return self.project.id

    def __init__(self, manager: type[ProjectProcessor], project: ProjectTable) -> None:
        self.project = project
        self.sub_tasks = {}
        self.changes = []
        self._listeners = []
        self._manager = manager

    def subscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        self._listeners.append(queue)

    def unsubscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        with suppress(ValueError):
            self._listeners.remove(queue)

    _is_waiting: bool = False

    async def update_sub_task(self, st: SubTask) -> None:
        self.changes.append(
            {"file_id": str(st.id), "content": st._content, "status": st._status}
        )
        if self._is_waiting:
            return
        await self._notify_listeners("update")

    async def _notify_listeners(
        self,
        message: str,
        stop_connections: bool = False,
    ) -> None:
        self._is_waiting = True
        await asyncio.sleep(1)
        self._is_waiting = False
        updates = self.changes.copy()
        self.changes.clear()
        queues = self._listeners.copy()

        tasks_len = len(self.sub_tasks)
        completed_len = 0
        # task_statuses = {}
        # for t, s in self.sub_tasks.items():
        #     if s == ProcessingStatus.completed:
        #         completed_len += 1
        #     task_statuses[t.id] = s

        log = TaskLog(
            project_id=self.project.id,
            status=self.project.status,
            completed_tasks=completed_len,
            total_tasks=tasks_len,
            message=message or "",
            error=None,
            task_statuses=updates,
            stop_connections=stop_connections,
        )

        for q in queues:
            await q.put(log)

    async def _on_sub_task_update(self, log: SubTaskLog, task: SubTask) -> None:
        self.sub_tasks[task] = log.status
        await self.update_sub_task(task)
        # await self._notify_listeners(log.message)

    async def _run_task(self, task: SubTask) -> SubTask:
        t0 = time.perf_counter()
        await task.start()
        logger.debug(
            f"Transcription for file {task.id} finished (took {(time.perf_counter() - t0):.4f}s)"
        )
        # Commit immediately to emit SSE event for real-time UI update
        task.commit()
        return task

    async def start(self) -> None:
        db = ProjectRepo.instance.get_session()()
        project = await ProjectRepo.instance.get_project_or_404(
            db, self.project.id, self.project.created_by
        )
        if project.status != ProcessingStatus.pending:
            msg = (
                f"Cannot start non-pending project {project.id}. "
                f"(current {project.status})"
            )
            raise RuntimeError(msg)

        t0 = time.perf_counter()
        logger.info(f"Processing started for project {self.project.id}")
        await self._notify_listeners("Started")

        files = project.files

        self.project.status = ProcessingStatus.processing
        await ProjectRepo.instance.replace_project(
            db, self.project, self.project.created_by
        )
        EventManager.notify(
            ProjectEvent.from_table(
                self.project, str(self.project.created_by), EventType.project_updated
            )
        )

        for file in files:
            t = SubTask(db, file)
            t.listener = self._on_sub_task_update
            self.sub_tasks[t] = file.transcription_status

        sem = asyncio.Semaphore(Config.MAX_TASKS_PER_PROJECT)
        tasks: list[Coroutine[Any, Any, SubTask]] = []

        async def run_limited(st: SubTask) -> SubTask:
            async with sem:
                return await self._run_task(st)

        for st, status in self.sub_tasks.items():
            if status == ProcessingStatus.pending:
                tasks.append(run_limited(st))

        results = await asyncio.gather(*tasks)
        self.project.status = ProcessingStatus.completed

        # Files are already committed in _run_task, no need to commit again

        await ProjectRepo.instance.replace_project(
            db, self.project, self.project.created_by
        )

        self._manager.on_task_complete(self.id)
        await self._notify_listeners("Finished", stop_connections=True)
        logger.info(
            f"Transcription finished for project {self.id} "
            f"(took {(time.perf_counter() - t0):.4f}s)"
        )
        EventManager.notify(
            ProjectEvent.from_table(
                self.project, str(self.project.created_by), EventType.project_updated
            )
        )
