from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.entities.models.audio_file import AudioFileTable

class UpdateAudioFileSchema(BaseModel):
    file_name: str | None = Field(None, min_length=1, max_length=32)

    def update(self, file: AudioFileTable):
        if self.file_name:
            *file_names, ext = file.file_name.split('.')
            file.file_name = f'{self.file_name}.{ext}'
