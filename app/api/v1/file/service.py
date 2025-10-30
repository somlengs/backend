import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

from fastapi import UploadFile, HTTPException, status
from pydub import AudioSegment


from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.types.enums.processing_status import ProcessingStatus


async def add_file_to_project(
    user_id: UUID | str,
    file: UploadFile,
    project: ProjectTable,
    file_name: str | None = None,
) -> ProjectTable:
    if not file.filename or not file.filename.endswith('.wav'):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            'Invalid wave file',
        )

    data = await file.read()

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_path = tmp_path / file.filename
        with file_path.open('wb') as f:
            f.write(data)

        id = uuid4()
        now = datetime.datetime.now(datetime.UTC)

        audio_data = AudioSegment.from_file(file_path)
        duration_ms = len(audio_data)
        path_raw = f'{project.id}/raw/{file_path.name}'
        audio_file = AudioFileTable(
            id=id,
            project_id=project.id,
            created_by=UUID(user_id) if user_id is str else user_id,
            file_name=file_path.name,
            file_path_raw=path_raw,
            file_size=file_path.stat().st_size,
            duration=duration_ms,
            format='wav',
            transcription_status=ProcessingStatus.draft,
            created_at=now,
            updated_at=now,
        )
        project.files.append(audio_file)

    return project
