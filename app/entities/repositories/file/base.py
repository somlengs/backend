from __future__ import annotations

from abc import ABC, abstractmethod
from io import BufferedReader, FileIO
from pathlib import Path

from storage3.types import UploadResponse



class FileRepo(ABC):

    instance: FileRepo

    @classmethod
    def init(cls, repo: FileRepo) -> None:
        cls.instance = repo

    @abstractmethod
    async def upload(
        self,
        data: BufferedReader | bytes | FileIO | str | Path,
        file_path: str,
    ) -> UploadResponse:
        ...

    @abstractmethod
    async def download(
        self,
        file_path: str,
        local_path: str | Path,
    ) -> bytes:
        ...

    @abstractmethod
    async def move(
        self,
        file_path: str,
        dest_path: str,
    ) -> bytes:
        ...

    @abstractmethod
    async def delete(
        self,
        file_path: str,
    ) -> bytes:
        ...
