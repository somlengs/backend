import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID, uuid4

from fastapi import UploadFile, HTTPException, status
from pydub import AudioSegment


from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.types.enums.processing_status import ProcessingStatus
from app.shared.utils.other import bump_name, convert_to_wav


async def add_file_to_project(
    user_id: UUID | str,
    file: UploadFile,
    project: ProjectTable,
) -> tuple[ProjectTable, AudioFileTable]:
    if not file.filename:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            'Invalid file',
        )
        
    data = await file.read()

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_path = tmp_path / file.filename
        with file_path.open('wb') as f:
            f.write(data)
        wav_file = await convert_to_wav(file_path)

        id = uuid4()
        now = datetime.datetime.now(datetime.UTC)

        audio_data = AudioSegment.from_file(wav_file)
        duration_ms = len(audio_data)
        file_name = await generate_file_name(project.id, file_path.name)
        supa_path = f'{project.id}/raw/{file_name}'
        audio_file = AudioFileTable(
            id=id,
            project_id=project.id,
            created_by=UUID(user_id) if user_id is str else user_id,
            file_name=file_name,
            file_path_raw=supa_path,
            file_size=wav_file.stat().st_size,
            duration=duration_ms,
            format='wav',
            transcription_status=ProcessingStatus.pending,
            created_at=now,
            updated_at=now,
        )
        with wav_file.open('rb') as f:
            await SSSRepo.instance.upload(f, file_path=supa_path)
        project.files.append(audio_file)
        if project.status == ProcessingStatus.completed:
            project.status = ProcessingStatus.pending

    return project, audio_file


async def generate_file_name(
    project_id: UUID | str,
    name_with_ext: str,
) -> str:
    path_raw = f'{project_id}/raw/{name_with_ext}'
    if not await SSSRepo.instance.exists(path_raw):
        return name_with_ext
    i = 1
    *names, ext = name_with_ext.split('.')
    while True:
        name = bump_name(names[-1], i)
        path_raw = f'{project_id}/raw/{name}.{ext}'
        if not await SSSRepo.instance.exists(path_raw):
            return f'{name}.{ext}'
        i += 1
