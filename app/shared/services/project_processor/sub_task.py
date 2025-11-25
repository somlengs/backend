from __future__ import annotations

from collections.abc import Callable, Coroutine
from logging import Logger
from typing import Any, override
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logger import get as get_logger
from app.entities.models.audio_file import AudioFileTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.repositories.stt.base import STTRepo
from app.entities.schemas.events.audio_file_event import AudioFileEvent
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.task_log import SubTaskLog
from app.entities.types.transcription_result import TranscriptionResult
from app.shared.services.event_manager import EventManager


class SubTask:
    file: AudioFileTable
    db: Session

    listener: Callable[[SubTaskLog, SubTask], Coroutine[Any, Any, None]] | None = None

    _status: ProcessingStatus
    _content: str | None
    _progress: float | None = None
    _error_msg: str | None = None

    result: TranscriptionResult | None = None

    logger: Logger

    @property
    def id(self) -> UUID:
        return self.file.id

    def __init__(self, db: Session, file: AudioFileTable) -> None:
        self.file = file
        self.db = db
        self._load()
        self.logger = get_logger()

    async def _log(self, msg: str) -> None:
        log = SubTaskLog(
            file_id=self.id,
            status=self._status,
            message=msg,
            progress=self._progress,
            error=None,
        )
        if self.listener is not None:
            await self.listener(log, self)
        self.logger.info(log)

    async def _err(self, msg: str, code: int = 500) -> None:
        log = SubTaskLog(
            file_id=self.id,
            status=self._status,
            message=msg,
            progress=None,
            error=code,
        )
        if self.listener is not None:
            await self.listener(log, self)
        self.logger.error(log)

    def _load(self) -> None:
        self._status = self.file.transcription_status
        self._content = self.file.transcription_content
        self._progress = None  # Unimplemented

    def commit(self) -> None:
        self.file.transcription_status = self._status
        self.file.transcription_content = self._content
        EventManager.notify(
            AudioFileEvent.from_table(
                self.file,
                str(self.file.project_id),
                EventType.file_updated,
                SSSRepo.instance.get_public_url(self.file.file_path_raw),
            )
        )
        self.db.merge(self.file)

    async def start(self) -> None:
        if self._status != ProcessingStatus.pending:
            raise RuntimeError(f"Cannot process already started file {self.id}")

        self._status = ProcessingStatus.processing
        await self._log(f"File {self.file.file_name} started")

        self.result = await STTRepo.instance.transcribe_from_sss_path(
            self.file.file_path_raw
        )

        if self.result.status_code == 201:
            self._status = ProcessingStatus.completed
            self._content = self.result.transcription
            await self._log(f"File {self.file.file_name} finished")

        else:
            self._status = ProcessingStatus.error
            self._progress = None
            msg = "Failed to transcribe"
            self._error_msg = msg
            await self._err(
                f"File {self.file.file_name} failed", code=self.result.status_code
            )

    def _save_to_db(self) -> None:
        self.db.commit()

    @override
    def __eq__(self, value: object) -> bool:
        return isinstance(value, SubTask) and self.id == value.id

    @override
    def __hash__(self) -> int:
        return self.id.__hash__()
