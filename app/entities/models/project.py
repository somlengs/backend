import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, object_session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from app.entities.types.enums.processing_status import ProcessingStatus

from .__base__ import Base

from .audio_file import AudioFileTable
if TYPE_CHECKING:
    from .auth_user import AuthUserTable


class ProjectTable(Base):
    __tablename__ = 'projects'

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    status: Mapped[ProcessingStatus] = mapped_column(
        nullable=False,
        default=ProcessingStatus.loading,
    )
    progress: Mapped[int] = mapped_column(nullable=False, default=0)
    project_path: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.now
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            'auth.users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )

    # Relationships
    files: Mapped[list['AudioFileTable']] = relationship(
        'AudioFileTable',
        uselist=True,
        back_populates='project',
        cascade='all, delete-orphan',
        passive_deletes=True,
        primaryjoin='ProjectTable.id==AudioFileTable.project_id',
    )
    user: Mapped['AuthUserTable'] = relationship(
        'AuthUserTable',
        uselist=False,
        back_populates='projects',
    )

    # Properties
    @hybrid_property
    def num_of_files(self) -> int:
        session = object_session(self)
        if session is None or self.id is None:
            return len(self.files) if self.files is not None else 0

        return session.scalar(
            select(func.count(AudioFileTable.id)).where(AudioFileTable.project_id == self.id)
        ) or 0
