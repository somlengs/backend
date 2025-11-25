import datetime
import uuid
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast
from zipfile import ZipFile

from fastapi import HTTPException, UploadFile, status
import httpx
from pydub import AudioSegment
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import exc

from app.core.config import Config
from app.core.logger import get as get_logger
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.repositories.file.base import AudioFileRepo
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.sss.base import SSSRepo
from app.entities.schemas.auth_user import AuthUser
from app.entities.schemas.events.audio_file_event import AudioFileEvent
from app.entities.schemas.events.project_event import ProjectEvent
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.processing_status import ProcessingStatus
from app.shared.services.event_manager import EventManager
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
        logger.debug(f'Service initialized project_id={self.id}')

    def validate_data(self) -> None:
        for file in self.files:
            if not file.filename or not file.filename.endswith('.zip'):
                logger.error(f'Validation failed: {file.filename} is not a ZIP file')
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    'Invalid zip file'
                )
        logger.debug('File validation passed')

    def close(self) -> None:
        logger.debug('Closing DB session and cleaning temp folder')
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
        logger.debug(f'Project instance created id={self.id}')

    async def upload_project(self) -> None:
        await ProjectRepo.instance.add_project(self.db, self.project)
        logger.debug(f'Empty project uploaded to supabase. id={self.id}')

    async def extract_zip(self) -> None:
        t0 = time.perf_counter()
        logger.info('Extracting zip files')

        for zip_file in self.files:
            logger.debug(f'Processing zip: {zip_file.filename}')
            tmp_path = Path(self.tmp_folder.name)
            zip_path = tmp_path / cast(str, zip_file.filename)

            with zip_path.open('wb') as z:
                data = await zip_file.read()
                z.write(data)
                logger.debug(f'Wrote zip to disk ({len(data):_} bytes) -> {zip_path}')

            with ZipFile(zip_path, 'r') as z:
                z.extractall(self.tmp_folder.name)

                audio_files = [
                    f for f in z.namelist()
                    if f.lower().endswith(Config.SUPPORTED_AUDIO_EXTS)
                    and not f.startswith('__MACOSX/')
                    and not f.endswith('.ds_store')
                ]

                logger.info(f'Found {len(audio_files)} audio candidates in zip')

                for file in audio_files:
                    try:
                        source = tmp_path / file
                        logger.debug(f'Converting to wav: {source.name}')
                        wav_file = await convert_to_wav(source)
                        self.files_to_process.append(wav_file)
                    except Exception:
                        logger.error(f'Failed to convert {file}', exc_info=True)
                self.project.initial_num_of_files = len(audio_files)

        logger.info(f'Extraction completed: {len(self.files_to_process)} files ready ({(time.perf_counter() - t0):.4f}s)')
        EventManager.notify(ProjectEvent.from_table(self.project, str(self.user.id), EventType.project_created))

    async def upload_files(self) -> None:
        t0 = time.perf_counter()
        logger.info(f'Uploading {len(self.files_to_process)} file(s) for project {self.id}')

        try:
            for idx, file in enumerate(self.files_to_process, 1):
                f0 = time.perf_counter()
                logger.debug(f'[{idx}/{len(self.files_to_process)}] Processing {file.name}')

                supa_path = f'{self.id}/raw/{file.name}'
                
                try:
                    with file.open('rb') as f:
                        logger.debug(f'Uploading raw file -> {supa_path}')
                        await SSSRepo.instance.upload(f, file_path=supa_path)
                except httpx.ReadTimeout:
                    logger.warning(f'Failed to upload {file.name} to supabase. Skipped')
                    self.project.initial_num_of_files = self.project.initial_num_of_files - 1
                    continue

                audio_segment = AudioSegment.from_file(str(file))
                duration_ms = len(audio_segment)
                audio_id = uuid.uuid4()

                audio = AudioFileTable(
                    id=audio_id,
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
                logger.debug(f'Indexed {file.name} ({duration_ms}ms, id={audio_id}) in {(time.perf_counter() - f0):.4f}s')
                EventManager.notify(AudioFileEvent.from_table(audio, str(self.id) + str(self.project.id), EventType.file_created, SSSRepo.instance.get_public_url(supa_path)))
                await AudioFileRepo.instance.add_file(self.db, audio)

            self.project.files = self.processed_files
            self.project.status = ProcessingStatus.pending

            logger.info('Persisting processed file metadata to DB')
            await ProjectRepo.instance.replace_project(self.db, self.project, self.user.id)
            EventManager.notify(ProjectEvent.from_table(self.project, self.user.id, EventType.project_updated))

            logger.info(
                f'Processed {len(self.processed_files)} files for project {self.id} ({(time.perf_counter() - t0):.4f}s)'
            )

        except Exception:
            logger.error('File processing pipeline failed', exc_info=True)
            raise

        finally:
            self.close()
