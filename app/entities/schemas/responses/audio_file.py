from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.entities.types.enums.processing_status import ProcessingStatus


class ProjectAudioFileDetailResponse(BaseModel):
    id: UUID
    file_name: str
    file_path_raw: str
    file_path_cleaned: str | None
    file_size: int | None
    duration: int | None
    format: str | None
    transcription_status: ProcessingStatus | None
    transcription_content: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
