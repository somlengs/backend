import asyncio
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from uuid import UUID
from typing import Annotated

import fastapi as api
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from .services import *
from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
from app.core.logger import get as get_logger
from app.entities.dto.responses.audio_file import audio_file_model_to_schema
from app.entities.dto.responses.project import project_model_to_schema
from app.entities.schemas.auth_user import AuthUser
from app.entities.schemas.params.listing.project import ProjectListingParams
from app.entities.schemas.requests.project import UpdateProjectSchema
from app.entities.types.enums.ordering import Ordering
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.enums.sorting import ProjectSorting
from app.entities.types.pagination import Paginated
from app.entities.models.project import ProjectTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.responses.project import Project
from app.shared.utils.other import paginate


router = api.APIRouter(prefix='/project')

logger = get_logger()


@router.post('/')
async def new_project(
    files: list[api.UploadFile],
    background: api.BackgroundTasks,
    name: str = api.Form('New Project'),
    description: str | None = api.Form(None),
    user: AuthUser = api.Depends(auth_user),
):
    service = NewProjectService(
        files,
        name,
        description,
        user,
    )
    try:
        service.validate_data()
        
        service.create_project_instance()
        await service.upload_project()
        await service.extract_zip()
        
        num_of_files = len(service.files_to_process)

        background.add_task(service.process_files)
        res = project_model_to_schema(service.project)
        res.num_of_files = num_of_files
        return res
    except Exception:
        service.close()
        raise
        

@router.get('/')
async def get_all(
    offset: int = api.Query(0, ge=0),
    limit: int = api.Query(20, ge=1),
    name: str = api.Query(''),
    status: ProcessingStatus | None = api.Query(None),
    sort: ProjectSorting = api.Query(ProjectSorting.updated_at),
    order: Ordering = api.Query(Ordering.desc),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
) -> Paginated[Project]:
    all = await ProjectRepo.instance.get_all_projects_for_user(
        db,
        user.id,
        ProjectListingParams(
            project_name=name,
            status=status,
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
        )
    )

    return {
        'data': [project_model_to_schema(x) for x in all['data']],
        'pagination': all['pagination']
    }


@router.get('/{project_id}')
async def get(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.get_project_by_id(
        db,
        str(project_id),
        user.id,
    )

    if project is not None:
        return project_model_to_schema(project)

    raise api.HTTPException(
        api.status.HTTP_404_NOT_FOUND,
        'Project not found'
    )


@router.patch('/{project_id}')
async def patch(
    project_id: UUID,
    body: UpdateProjectSchema,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.update_project(
        db,
        project_id,
        user.id,
        **body.model_dump()
    )

    if project is not None:
        return project_model_to_schema(project)

    raise api.HTTPException(
        api.status.HTTP_404_NOT_FOUND,
        'Project not found'
    )


@router.delete('/{project_id}')
async def delete(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    did_delete = await ProjectRepo.instance.delete_project(
        db,
        project_id,
        user.id,
    )

    if did_delete:
        return api.responses.JSONResponse(
            status_code=api.status.HTTP_200_OK,
            content={'detail': 'Project deleted successfully'}
        )

    raise api.HTTPException(
        api.status.HTTP_404_NOT_FOUND,
        'Project not found'
    )


@router.post('/{project_id}/process')
async def process_project(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.get_project_by_id(
        db,
        str(project_id),
        user.id,
    )

    if project is None:
        raise api.HTTPException(
            api.status.HTTP_404_NOT_FOUND,
            'Project not found'
        )
    # return api.responses.StreamingResponse(
    #     simulate_task_progress(project_id),
    #     media_type="text/event-stream",
    # )
    ...


@router.get('/{project_id}/download')
async def download_project(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.get_project_by_id(
        db,
        str(project_id),
        user.id,
    )

    if project is None:
        raise api.HTTPException(
            api.status.HTTP_404_NOT_FOUND,
            'Project not found'
        )
    ...
