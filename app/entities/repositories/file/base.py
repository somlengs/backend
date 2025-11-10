from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID
from collections.abc import Callable

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from app.entities.models.audio_file import AudioFileTable
from app.entities.schemas.params.listing.audio_file import AudioFileListingParams
from app.entities.schemas.requests.audio_file import UpdateAudioFileSchema
from app.entities.types.pagination import Paginated


class AudioFileRepo(ABC):

    instance: AudioFileRepo

    @classmethod
    def init(cls, repo: AudioFileRepo) -> None:
        cls.instance = repo

    @abstractmethod
    def get_session(self) -> sessionmaker[Session]:
        ...

    @abstractmethod
    async def get_files_for_project[T](
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
        params: AudioFileListingParams,
        *,
        mapper: Callable[[AudioFileTable], T] = lambda x: x,
    ) -> Paginated[T]:
        ...

    @abstractmethod
    async def get_file_by_id(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
    ) -> AudioFileTable | None:
        ...

    async def get_project_or_404(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
    ) -> AudioFileTable:
        file = await self.get_file_by_id(
            db,
            file_id,
            user_id,
        )

        if file is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                'File not found',
            )

        return file

    @abstractmethod
    async def create_file(self, db: Session, project_id: UUID | str, user_id: UUID | str, **kwargs) -> AudioFileTable:
        ...

    @abstractmethod
    async def add_file(self, db: Session, file: AudioFileTable) -> None:
        ...

    @abstractmethod
    async def update_file(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
        data: UpdateAudioFileSchema,
    ) -> AudioFileTable | None:
        ...

    @abstractmethod
    async def replace_file(
        self,
        db: Session,
        file: AudioFileTable,
        user_id: UUID | str,
        exists_only: bool = False,
    ) -> AudioFileTable:
        ...

    @abstractmethod
    async def delete_file(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
    ) -> bool:
        ...
