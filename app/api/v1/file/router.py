
from uuid import UUID
import fastapi as api
from supabase_auth import Session

from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
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
    ...


@router.patch('/{project_id}/files/{file_id}')
async def edit_file(
    project_id: UUID,
    file_id: UUID,
    body: UpdateAudioFileSchema,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    ...


@router.delete('/{project_id}/files/{file_id}')
async def remove_file(
    project_id: UUID,
    file_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    ...
