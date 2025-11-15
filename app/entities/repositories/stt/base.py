from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.entities.types.transcription_result import TranscriptionResult


class STTRepo(ABC):
    """Speech-to-text Repository"""

    instance: STTRepo

    @classmethod
    def init(cls, repo: STTRepo) -> None:
        cls.instance = repo

    @abstractmethod
    async def transcribe_from_sss_path(self, path: str) -> TranscriptionResult:
        ...

    @abstractmethod
    async def transcribe_from_bytes(self, data: bytes, format: str = 'wav') -> TranscriptionResult:
        ...

    @abstractmethod
    async def transcribe_from_local_path(self, path: Path) -> TranscriptionResult:
        ...
