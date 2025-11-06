from app.entities.models.audio_file import AudioFileTable
from app.entities.schemas.responses.audio_file import ProjectAudioFileDetailResponse


def audio_file_model_to_schema(file: AudioFileTable) -> ProjectAudioFileDetailResponse:
    return ProjectAudioFileDetailResponse(
        id=file.id,
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
