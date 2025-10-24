from tempfile import TemporaryDirectory
from zipfile import ZipFile
from uuid import UUID

import fastapi as api
from sqlalchemy.orm import Session

from app.api.v1.project import service
from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
from app.entities.dto.responses.audio_file import audio_file_model_to_schema
from app.entities.dto.responses.project import project_model_to_schema
from app.entities.schemas.auth_user import AuthUser
from app.entities.types.pagination import Paginated
from app.entities.models.project import ProjectTable
from app.entities.models.auth_user import AuthUserTable
from app.entities.models.processing_log import ProcessingLogTable
from app.entities.models.audio_file import AudioFileTable
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.responses.project import ProjectListingResponse
from app.shared.utils.other import paginate


router = api.APIRouter(prefix='/project')


@router.post('/')
async def post(
    file: api.UploadFile = api.File(...),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):

    new_project = service.create_project(UUID(user.id))

    files = await service.extract_zip(file, new_project.id, UUID(user.id))

    new_project.files = files
    await ProjectRepo.instance.add_project(db, new_project)
    return project_model_to_schema(new_project)


@router.get('/')
async def get_all(
    skip: int = api.Query(0, ge=0),
    limit: int = api.Query(20, ge=1),
    status: str | None = api.Query(default=None),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
) -> Paginated[ProjectListingResponse]:
    all = await ProjectRepo.instance.get_all_projects_for_user(
        db,
        user.id,
        status=status,
    )

    return paginate(list(map(project_model_to_schema, all)), skip=skip, limit=limit)


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
