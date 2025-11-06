from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from collections.abc import Callable, AsyncGenerator
from typing import Any
from contextlib import suppress

from sqlalchemy.orm import Session

from app.entities.models.audio_file import AudioFileTable
from app.entities.models.processing_log import ProcessingLogTable
from app.entities.models.project import ProjectTable
from app.entities.types.enums.processing_status import ProcessingStatus


@dataclass
class SubTask:
    file: AudioFileTable


@dataclass
class TaskLog:
    status: ProcessingStatus
    completed_task: int
    total_tasks: int
    current_task_progress: float | None
    message: str = field(default='')
    error: str | None = field(init=False, default=None)


class ProcessingTask:
    project: ProjectTable
    sub_tasks: list[SubTask]
    logs: list[ProcessingLogTable]

    _listeners: list[asyncio.Queue[TaskLog]]

    def __init__(self, project: ProjectTable) -> None:
        self.project = project
        self.sub_tasks = []
        self.logs = []
        self._listeners = []

    def subscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        self._listeners.append(queue)

    def unsubscribe(self, queue: asyncio.Queue[TaskLog]) -> None:
        with suppress(ValueError):
            self._listeners.remove(queue)

    def _notify_listeners(
        self,
        message: str | None = None,
        error: str | None = None
    ) -> None:
        queues = self._listeners.copy()
        # log = TaskLog()

        # for q in queues:
            # q.put()
        ...

    async def _run_task(self) -> None:
        ...

    def start(self) -> None:
        ...
