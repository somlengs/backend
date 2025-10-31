from __future__ import annotations

import asyncio
import uuid

from sqlalchemy.orm import Session

from app.entities.models.project import ProjectTable


class ProjectProcessor:
    instance: ProjectProcessor

    def __init__(self) -> None:
        self.tasks: dict[str, asyncio.Task] = {}
        self.listeners: dict[str, list[asyncio.Queue[str]]] = {}

    @classmethod
    def init(cls):
        cls.instance = cls()

    async def process_task(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        db: Session,
    ):
        ...

    def _notify_listeners(self, task_id: str) -> None:
        ...

    def _update_task_status(self):
        ...
