from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Config
from app.core.logger import get
from app.entities.repositories.file.base import AudioFileRepo
from app.entities.repositories.file.supabase import SupabaseAudioFileRepo
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.project.supabase import SupabaseProjectRepo
from app.entities.repositories.sss.base import SSSRepo
from app.entities.repositories.sss.supabase import SupabaseSSSRepo
from app.entities.repositories.stt.base import STTRepo
from app.entities.repositories.stt.external import ExternalSTTRepo
from app.entities.repositories.stt.mock import MockSTTRepo


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get()
    ProjectRepo.init(SupabaseProjectRepo())
    AudioFileRepo.init(SupabaseAudioFileRepo())
    SSSRepo.init(SupabaseSSSRepo)
    STTRepo.init(ExternalSTTRepo())
    yield
    logger.warning('Server shut down')
