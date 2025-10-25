from __future__ import annotations
from io import BufferedReader, BytesIO, FileIO
from pathlib import Path
from typing import override

from supabase import Client, create_client
from storage3.types import UploadResponse

from app.core.config import Config
from app.entities.types.pagination import Paginated
from app.entities.models.project import ProjectTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable
from .base import FileRepo


class SupabaseFileRepo(FileRepo):

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
        return self.bucket.upload(file_path, data, file_options={'content-type': 'audio/wav'})

    @override
    async def download(
        self,
        file_path: str,
        local_path: str | Path,
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
    async def delete(
        self,
        file_path: str,
    ) -> bytes:
        ...
