import uuid
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .__base__ import Base

if TYPE_CHECKING:
    from .audio_file import AudioFileTable
    from .project import ProjectTable


class AuthUserTable(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    # Relationships
    files: Mapped[list['AudioFileTable']] = relationship(
        'AudioFileTable',
        uselist=True,
        back_populates='user',
    )
    projects: Mapped[list['ProjectTable']] = relationship(
        'ProjectTable',
        uselist=True,
        back_populates='user',
    )
