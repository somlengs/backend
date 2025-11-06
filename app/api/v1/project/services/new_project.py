import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast
import uuid
from zipfile import ZipFile

from fastapi import HTTPException, UploadFile, status
from pydub import AudioSegment
from sqlalchemy.orm import Session

from app.core.config import Config
from app.core.logger import get as get_logger
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.sss.base import SSSRepo
from app.entities.schemas.auth_user import AuthUser
from app.entities.types.enums.processing_status import ProcessingStatus
from app.shared.utils.other import convert_to_wav

logger = get_logger()


class NewProjectService:
    # Params
    files: list[UploadFile]
    name: str
    description: str | None
    user: AuthUser

    # Data
    id: uuid.UUID
    now: datetime.datetime
    project: ProjectTable
    db: Session
    tmp_folder: TemporaryDirectory
    files_to_process: list[Path]
    processed_files: list[AudioFileTable]

    def __init__(
        self,
        files: list[UploadFile],
        name: str,
        description: str | None,
        user: AuthUser,
    ) -> None:
        self.files = files
        self.name = name
        self.description = description
        self.user = user
        self.__post_init__()

    def __post_init__(self) -> None:
        self.id = uuid.uuid4()
        self.now = datetime.datetime.now(datetime.UTC)
        self.db = ProjectRepo.instance.get_session()()
        self.tmp_folder = TemporaryDirectory()
        self.files_to_process = []
        self.processed_files = []

    def validate_data(self) -> None:
        for file in self.files:
            if not file.filename or not file.filename.endswith('.zip'):
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    'Invalid zip file'
                )

    def close(self) -> None:
        self.db.close()
        self.tmp_folder.cleanup()

    def create_project_instance(self) -> None:
        self.project = ProjectTable(
            id=self.id,
            name=self.name,
            description=self.description,
            status=ProcessingStatus.loading,
            progress=0,
            project_path=str(self.id),
            created_at=self.now,
            updated_at=self.now,
            created_by=self.user.id,
        )

    async def upload_project(self) -> None:
        await ProjectRepo.instance.add_project(self.db, self.project)

    async def process_files(self) -> None:
        logger.info(f'Processing {len(self.files_to_process)} file(s) ({self.id})')
        try:
            for file in self.files_to_process:
                supa_path = f'{self.id}/raw/{file.name}'
                with file.open('rb') as f:
                    await SSSRepo.instance.upload(f, file_path=supa_path)
                audio_segment = AudioSegment.from_file(str(file))
                duration_ms = len(audio_segment)
                id = uuid.uuid4()

                audio = AudioFileTable(
                    id=id,
                    project_id=self.id,
                    created_by=self.user.id,
                    file_name=file.name,
                    file_path_raw=supa_path,
                    file_size=file.stat().st_size,
                    duration=duration_ms,
                    format=file.suffix.removeprefix('.'),
                    transcription_status=ProcessingStatus.pending,
                    created_at=self.now,
                    updated_at=self.now,
                )
                self.processed_files.append(audio)

            self.project.files = self.processed_files
            self.project.status = ProcessingStatus.pending

            await ProjectRepo.instance.replace_project(
                self.db,
                self.project,
                self.user.id,
            )
            logger.info(f'Processed {len(self.processed_files)} file(s) ({self.id})')
        finally:
            self.close()

    async def extract_zip(self) -> None:
        for zip_file in self.files:
            tmp_path = Path(self.tmp_folder.name)
            zip_path = tmp_path / cast(str, zip_file.filename)
            with zip_path.open('wb') as z:
                z.write(await zip_file.read())

            with ZipFile(zip_path, 'r') as z:
                z.extractall(self.tmp_folder.name)
                audio_files = [
                    f for f in z.namelist()
                    if f.lower().endswith(Config.SUPPORTED_AUDIO_EXTS)
                    and not f.startswith('__MACOSX/')
                    and not f.endswith('.ds_store')
                ]

                for file in audio_files:
                    wav_file = await convert_to_wav(tmp_path / file)

                    self.files_to_process.append(wav_file)
