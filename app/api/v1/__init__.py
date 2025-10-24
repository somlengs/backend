from importlib import import_module
from pathlib import Path

from fastapi import FastAPI, APIRouter

def load_routers(app: FastAPI) -> None:

    version_router = APIRouter(prefix='/v1', tags=['Version 1'])
    
    api_dir = Path(__file__).parent
    for pkg in api_dir.iterdir():
        if not pkg.is_dir():
            continue

        router_file = pkg / 'router.py'

        if not router_file.exists():
            continue

        module = import_module(f'app.api.v1.{pkg.name}.router')
        router = getattr(module, 'router', None)

        if router is not None:
            version_router.include_router(router)

    app.include_router(version_router)
