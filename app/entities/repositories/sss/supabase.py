from __future__ import annotations
import asyncio
from io import BufferedReader, FileIO
from pathlib import Path
from typing import override

from supabase import Client, create_client
from storage3.types import UploadResponse

from app.core.config import Config
from app.entities.models.project import ProjectTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.auth_user import AuthUserTable
from .base import SSSRepo


class SupabaseSSSRepo(SSSRepo):

    def __init__(self) -> None:
        self.client: Client = create_client(
            Config.Supabase.URL,
            Config.Supabase.SERVICE_ROLE
        )
        self.bucket = self.client.storage.from_(
            Config.Supabase.STORAGE_BUCKET_NAME
        )

    @override
    async def upload(
        self,
        data: BufferedReader | bytes | FileIO | str | Path,
        file_path: str,
    ) -> UploadResponse:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.bucket.upload(file_path, data, file_options={
                                       'content-type': 'audio/wav'})
        )

    @override
    async def download(
        self,
        file_path: str,
    ) -> bytes:
        return self.bucket.download(file_path)

    @override
    async def move(
        self,
        file_path: str,
        dest_path: str,
    ) -> bytes:
        ...

    @override
    async def bulk_delete(
        self,
        file_paths: list[str],
    ) -> None:
        if len(file_paths) <= 0:
            return
        self.bucket.remove(file_paths)

    @override
    async def exists(
        self,
        file_path: str,
    ) -> bool:
        return self.bucket.exists(file_path)
