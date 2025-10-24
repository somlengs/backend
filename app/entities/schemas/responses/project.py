from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.schemas.responses.audio_file import ProjectListingAudioFileResponse

class ProjectListingResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: ProcessingStatus
    progress: int
    project_path: str
    created_at: datetime
    updated_at: datetime
    files: list[ProjectListingAudioFileResponse]
