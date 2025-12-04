from collections.abc import Callable
from datetime import UTC, datetime
from typing import override
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Config
from app.core.logger import get
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.schemas.params.listing.audio_file import AudioFileListingParams
from app.entities.schemas.requests.audio_file import UpdateAudioFileSchema
from app.entities.types.pagination import Paginated
from app.shared.utils.query import paginate_query

from .base import AudioFileRepo

logger = get()


class SupabaseAudioFileRepo(AudioFileRepo):
    def __init__(self) -> None:
        self.engine = create_engine(Config.Supabase.DATABASE_URL)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

        super().__init__()

    @override
    def get_session(self) -> sessionmaker[Session]:
        return self.SessionLocal

    @override
    async def get_files_for_project[T](
        self,
        db: Session,
        project_id: UUID | str,
        user_id: UUID | str,
        params: AudioFileListingParams,
        *,
        mapper: Callable[[AudioFileTable], T] = lambda x: x,
    ) -> Paginated[T]:
        project = (
            db.query(ProjectTable)
            .filter(ProjectTable.created_by == user_id)
            .filter(ProjectTable.id == project_id)
            .one_or_none()
        )

        if project is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Project not found",
            )

        name: str = params.file_name
        f_status: str | None = params.status
        limit = params.limit
        page = params.page
        sort = params.sort
        order = params.order

        query = db.query(AudioFileTable).filter(AudioFileTable.project_id == project_id)

        if len(name) > 2:
            query = query.filter(
                func.lower(AudioFileTable.file_name).like(f"%{name.lower()}%")
            )

        if f_status is not None:
            query = query.filter(AudioFileTable.transcription_status == f_status)

        sort_col = sort.column()
        query = order.apply(query, sort_col)

        return paginate_query(db, query, limit, page, mapper=mapper)

    @override
    async def get_file_by_id(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
    ) -> AudioFileTable | None:
        return (
            db.query(AudioFileTable)
            .filter(AudioFileTable.id == file_id)
            .filter(AudioFileTable.created_by == user_id)
            .one_or_none()
        )

    async def get_file_or_404(
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
                "File not found",
            )

        return file

    @override
    async def create_file(
        self, db: Session, project_id: UUID | str, user_id: UUID | str, **kwargs
    ) -> AudioFileTable:
        file = AudioFileTable(project_id=project_id, created_by=user_id, **kwargs)
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @override
    async def add_file(self, db: Session, file: AudioFileTable) -> None:
        db.add(file)
        db.commit()
        db.refresh(file)

    @override
    async def update_file(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
        data: UpdateAudioFileSchema,
    ) -> AudioFileTable | None:
        file = await self.get_file_or_404(db, file_id, user_id)

        data.update(file)

        name_query = (
            db.query(AudioFileTable)
            .filter(AudioFileTable.project_id == file.project_id)
            .filter(AudioFileTable.id != file.id)
            .where(AudioFileTable.file_name == file.file_name)
        )
        if name_query.first():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Name already exists")
        db.commit()
        db.refresh(file)
        return file

    @override
    async def replace_file(
        self,
        db: Session,
        file: AudioFileTable,
        user_id: UUID | str,
        exists_only: bool = False,
    ) -> AudioFileTable:
        existing = await self.get_file_by_id(db, file.id, user_id)

        if existing is None:
            if exists_only:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    "File not found",
                )
            file.updated_at = datetime.now(UTC)
            db.add(file)
            db.commit()
            db.refresh(file)
            return file

        for column in ProjectTable.__table__.columns.keys():
            setattr(existing, column, getattr(file, column))
        existing.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(existing)
        return existing

    @override
    async def delete_file(
        self,
        db: Session,
        file_id: UUID | str,
        user_id: UUID | str,
    ) -> bool:
        file = await self.get_file_by_id(db, file_id, user_id)

        if file is None:
            return False

        db.delete(file)
        db.commit()
        logger.info(f"Deleted file {file.id} from project {file.project_id}")
        return True

    @override
    async def get_completed_files(
        self,
        db: Session,
        project_id: UUID | str,
    ) -> list[AudioFileTable]:
        from app.entities.types.enums.processing_status import ProcessingStatus
        
        files = (
            db.query(AudioFileTable)
            .filter(AudioFileTable.project_id == project_id)
            .filter(AudioFileTable.transcription_status == ProcessingStatus.completed)
            .all()
        )
        return files
