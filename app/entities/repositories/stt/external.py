import asyncio
from pathlib import Path
from typing import Any, override

import httpx

from app.core.config import Config
from app.entities.types.transcription_result import TranscriptionResult
from .base import STTRepo

class ExternalSTTRepo(STTRepo):

    @override
    async def transcribe_from_sss_path(self, path: str) -> TranscriptionResult:
        async with httpx.AsyncClient(timeout=httpx.Timeout(Config.ASR_TIMEOUT)) as client:
            res = await client.post(
                f'{Config.ASR_URL}/transcribe',
                params={
                    'audio_path': path
                }
            )
            
            data: dict[str, Any] = res.json()
            return TranscriptionResult(**data)

    @override
    async def transcribe_from_bytes(self, data: bytes, format: str = 'wav') -> TranscriptionResult:
        ...

    @override
    async def transcribe_from_local_path(self, path: Path) -> TranscriptionResult:
        ...
