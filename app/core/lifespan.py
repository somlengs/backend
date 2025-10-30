from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Config
from app.entities.repositories.sss.base import SSSRepo
from app.entities.repositories.sss.supabase import SupabaseSSSRepo
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.project.supabase import SupabaseProjectRepo

@asynccontextmanager
async def lifespan(app: FastAPI):
    ProjectRepo.init(SupabaseProjectRepo())
    SSSRepo.init(SupabaseSSSRepo())
    yield
    ...
