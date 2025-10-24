from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Config
from app.entities.repositories.file.base import FileRepo
from app.entities.repositories.file.supabase import SupabaseFileRepo
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.project.supabase import SupabaseProjectRepo

@asynccontextmanager
async def lifespan(app: FastAPI):
    ProjectRepo.init(SupabaseProjectRepo())
    FileRepo.init(SupabaseFileRepo())
    yield
    ...
