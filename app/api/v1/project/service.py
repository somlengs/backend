import asyncio
import datetime
from tempfile import TemporaryDirectory
from pathlib import Path
from zipfile import ZipFile
import uuid

from fastapi import UploadFile, HTTPException, status
from pydub import AudioSegment

from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.types.enums.processing_status import ProcessingStatus


def create_project(
    user_id: uuid.UUID,
    project_name: str = 'New Project',
    description: str | None = None,
) -> ProjectTable:
    id = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)
    project = ProjectTable(
        id=id,
        name=project_name,
        description=description,
        status=ProcessingStatus.draft,
        progress=0,
        project_path=str(id),
        created_at=now,
        updated_at=now,
        created_by=user_id,
    )
    return project


async def extract_zip(
    file: UploadFile,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[AudioFileTable]:
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            'Invalid zip file'
        )

    audio_objects: list[AudioFileTable] = []
    now = datetime.datetime.now(datetime.UTC)
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / file.filename
        with open(zip_path, 'wb') as f:
            f.write(await file.read())

        with ZipFile(zip_path, 'r') as zip_f:
            zip_f.extractall(tmp)
            wav_files = [
                f for f in zip_f.namelist()
                if f.lower().endswith('.wav')
            ]

            for wav in wav_files:
                file_path = tmp_path / wav
                path_raw = f'{project_id}/raw/{file_path.name}'

                with open(file_path, 'rb') as f:
                    await SSSRepo.instance.upload(f, file_path=path_raw)

                audio_segment = AudioSegment.from_file(file_path)
                duration_ms = len(audio_segment)

                id = uuid.uuid4()

                audio = AudioFileTable(
                    id=id,
                    project_id=project_id,
                    created_by=user_id,
                    file_name=file_path.name,
                    file_path_raw=path_raw,
                    file_size=file_path.stat().st_size,
                    duration=duration_ms,
                    format='wav',
                    transcription_status=ProcessingStatus.draft,
                    created_at=now,
                    updated_at=now,
                )
                audio_objects.append(audio)

    return audio_objects
