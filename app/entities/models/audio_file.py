from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.entities.types.enums.processing_status import ProcessingStatus

from .__base__ import Base

if TYPE_CHECKING:
    from .project import ProjectTable
    from .processing_log import ProcessingLogTable
    from .auth_user import AuthUserTable


class AudioFileTable(Base):
    __tablename__ = 'audio_files'

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_path_raw: Mapped[str] = mapped_column(nullable=False)
    file_size: Mapped[int | None]
    duration: Mapped[int | None]
    format: Mapped[str | None]
    transcription_status: Mapped[ProcessingStatus] = mapped_column(
        nullable=False, default=ProcessingStatus.pending
    )
    transcription_content: Mapped[str | None]
    error_message: Mapped[str | None]
    processing_started_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            'auth.users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    file_path_cleaned: Mapped[str | None]

    # Relationships
    project: Mapped['ProjectTable'] = relationship(
        'ProjectTable',
        uselist=False,
        back_populates='files',
    )
    logs: Mapped[list['ProcessingLogTable']] = relationship(
        'ProcessingLogTable',
        uselist=True,
        back_populates='file',
    )
    user: Mapped['AuthUserTable'] = relationship(
        'AuthUserTable',
        uselist=False,
        back_populates='files',
    )
