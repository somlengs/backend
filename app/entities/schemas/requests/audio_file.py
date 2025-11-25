from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

from app.entities.types.enums.processing_status import ProcessingStatus

if TYPE_CHECKING:
    from app.entities.models.audio_file import AudioFileTable

_FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class UpdateAudioFileSchema(BaseModel):
    file_name: str | None = Field(None, max_length=32)
    transcription_content: str | None = Field(None)

    @field_validator("file_name")
    @classmethod
    def valid_file_name(cls, file_name: str | None) -> str | None:
        if file_name is None or file_name == "":
            return None

        if file_name.lower() == ".wav":
            raise ValueError("Filename cannot be only .wav")

        if not _FILENAME_RE.match(file_name):
            raise ValueError("Invalid file_name characters")

        name, dot, ext = file_name.rpartition(".")
        if dot:
            ext = ext.lower()
            if ext != "wav":
                raise ValueError("Only .wav files are allowed")
            return f"{name}.{ext}"

        return f"{file_name}.wav"

    def update(self, file: AudioFileTable):
        if self.file_name:
            file.file_name = self.file_name
            file.updated_at = datetime.now(UTC)

        if self.transcription_content is not None:
            if file.transcription_status == ProcessingStatus.processing:
                return

            if self.transcription_content:
                file.transcription_content = self.transcription_content
                file.transcription_status = ProcessingStatus.completed

            else:
                file.transcription_content = None
                file.transcription_status = ProcessingStatus.pending

            file.updated_at = datetime.now(UTC)
