from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.entities.types.enums.processing_status import ProcessingStatus

from . import Base

if TYPE_CHECKING:
    from .audio_file import AudioFileTable
    from .auth_user import AuthUserTable


class ProcessingLogTable(Base):
    __tablename__ = 'processing_logs'

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    audio_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('audio_files.id', ondelete='CASCADE'),
        nullable=False,
    )
    operation: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str | None]
    status: Mapped[ProcessingStatus] = mapped_column(nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.now
    )
    completed_at: Mapped[datetime | None]
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            'auth.users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )

    # Relationships
    file: Mapped['AudioFileTable'] = relationship(
        'AudioFileTable',
        uselist=False,
        back_populates='logs',
    )
    user: Mapped['AuthUserTable'] = relationship(
        'AuthUserTable',
        uselist=False,
        back_populates='processing_logs',
    )
