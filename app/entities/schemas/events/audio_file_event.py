from datetime import datetime

from app.entities.models.audio_file import AudioFileTable
from app.entities.schemas.events.event import SEvent
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.processing_status import ProcessingStatus


class AudioFileEvent(SEvent):
    file_id: str | None
    """UUID as str"""
    project_id: str | None
    """Project UUID as str"""
    file_name: str | None
    public_url: str | None
    file_size: int | None
    duration: int | None
    format: str | None
    transcription_status: ProcessingStatus | None
    transcription_content: str | None
    created_at: datetime | None
    updated_at: datetime | None
    created_by: str | None
    """User UUID as str"""

    @classmethod
    def from_table(
        cls,
        audio: AudioFileTable,
        eid: str,
        event_type: EventType,
        public_url: str,
    ):
        return cls(
            eid=eid,
            event_type=event_type,
            file_id=str(audio.id),
            project_id=str(audio.project_id),
            file_name=audio.file_name,
            public_url=public_url,
            file_size=audio.file_size,
            duration=audio.duration,
            format=audio.format,
            transcription_status=audio.transcription_status,
            transcription_content=audio.transcription_content,
            created_at=audio.created_at,
            updated_at=audio.updated_at,
            created_by=str(audio.created_by),
        )

    @classmethod
    def no_data(
        cls,
        eid: str,
        event_type: EventType,
    ):
        return cls(
            eid=eid,
            event_type=event_type,
            file_id=None,
            project_id=None,
            file_name=None,
            public_url=None,
            file_size=None,
            duration=None,
            format=None,
            transcription_status=None,
            transcription_content=None,
            created_at=None,
            updated_at=None,
            created_by=None,
        )