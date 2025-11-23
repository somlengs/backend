from app.entities.models.audio_file import AudioFileTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.schemas.audio_file import AudioFile


def audio_file_model_to_schema(file: AudioFileTable) -> AudioFile:
    return AudioFile(
        id=file.id,
        project_id=file.project_id,
        file_name=file.file_name,
        file_path_raw=file.file_path_raw,
        file_path_cleaned=file.file_path_cleaned,
        file_size=file.file_size,
        duration=file.duration,
        format=file.format,
        transcription_status=file.transcription_status,
        transcription_content=file.transcription_content,
        error_message=file.error_message,
        created_at=file.created_at,
        updated_at=file.updated_at,
    )
