from uuid import UUID
import fastapi as api

from sqlalchemy.orm import Session

from app.api.v1.file import service
from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
from app.entities.dto.responses.project import project_model_to_schema
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.auth_user import AuthUser
from app.entities.schemas.requests.audio_file import UpdateAudioFileSchema


router = api.APIRouter(prefix='/project')


@router.post('/{project_id}/files')
async def add_file(
    project_id: UUID,
    file: api.UploadFile = api.File(...),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.get_project_by_id(
        db,
        project_id,
        user.id,
    )

    if project is None:
        raise api.HTTPException(
            api.status.HTTP_404_NOT_FOUND,
            'Project not found',
        )

    project = await service.add_file_to_project(
        user.id,
        file,
        project,
    )

    project = await ProjectRepo.instance.replace_project(
        db,
        project,
        user.id,
    )
    
    return project_model_to_schema(project)


@router.patch('/{project_id}/files/{file_id}')
async def edit_file(
    project_id: UUID,
    file_id: UUID,
    body: UpdateAudioFileSchema,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
): ...


@router.delete('/{project_id}/files/{file_id}')
async def remove_file(
    project_id: UUID,
    file_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
): ...
