from uuid import UUID

import fastapi as api
from sqlalchemy.orm import Session

from app.api.v1.file import service
from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
from app.core.logger import get
from app.entities.dto.responses.audio_file import audio_file_model_to_schema
from app.entities.dto.responses.project import project_model_to_schema
from app.entities.repositories.file.base import AudioFileRepo
from app.entities.repositories.project.base import ProjectRepo
from app.entities.repositories.sss.base import SSSRepo
from app.entities.schemas.audio_file import AudioFile
from app.entities.schemas.auth_user import AuthUser
from app.entities.schemas.events.audio_file_event import AudioFileEvent
from app.entities.schemas.params.listing.audio_file import AudioFileListingParams
from app.entities.schemas.requests.audio_file import UpdateAudioFileSchema
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.ordering import Ordering
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.enums.sorting import AudioFileSorting
from app.entities.types.pagination import Paginated
from app.shared.services.event_manager import EventManager

router = api.APIRouter(prefix="/project")
logger = get()


@router.get("/{project_id}/files/events")
async def files_events(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
) -> api.responses.StreamingResponse:
    _ = ProjectRepo.instance.get_project_or_404(
        db,
        project_id,
        user.id,
    )
    eid = user.id + str(project_id)
    gen = EventManager.get_stream(
        AudioFileEvent,
        lambda x: x.eid == eid,
    )
    return api.responses.StreamingResponse(
        gen,
        media_type="text/event-stream",
    )


@router.get("/{project_id}/files")
async def get_files(
    project_id: UUID,
    page: int = api.Query(1, ge=1),
    limit: int = api.Query(20, ge=1, le=1000),
    name: str = api.Query(""),
    status: ProcessingStatus | None = api.Query(None),
    sort: AudioFileSorting = api.Query(AudioFileSorting.file_name),
    order: Ordering = api.Query(Ordering.desc),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
) -> Paginated[AudioFile]:
    # project = await ProjectRepo.instance.get_project_or_404(
    #     db,
    #     project_id,
    #     user.id,
    # )

    # if project.status == ProcessingStatus.loading:
    #     raise api.HTTPException(
    #         api.status.HTTP_409_CONFLICT,
    #         "Current project is loading. Please wait."
    #     )

    files = await AudioFileRepo.instance.get_files_for_project(
        db,
        project_id,
        user.id,
        AudioFileListingParams(
            page=page,
            limit=limit,
            file_name=name,
            order=order,
            sort=sort,
            status=status,
        ),
        mapper=lambda x: audio_file_model_to_schema(x, ""),
    )

    for file in files["data"]:
        file.public_url = SSSRepo.create_instance().get_public_url(file.file_path_raw)

    return files


@router.post("/{project_id}/files")
async def add_file(
    project_id: UUID,
    file: api.UploadFile = api.File(...),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    project = await ProjectRepo.instance.get_project_or_404(
        db,
        project_id,
        user.id,
    )

    if project.status == ProcessingStatus.processing:
        raise api.HTTPException(
            api.status.HTTP_409_CONFLICT, "Current project is processing. Please wait."
        )

    project, audio_file = await service.add_file_to_project(
        user.id,
        file,
        project,
    )

    project = await ProjectRepo.instance.replace_project(
        db,
        project,
        user.id,
    )

    public_url = SSSRepo.create_instance().get_public_url(audio_file.file_path_raw)
    EventManager.notify(
        AudioFileEvent.from_table(
            audio_file,
            user.id + str(project_id),
            EventType.file_created,
            public_url=public_url,
        )
    )

    return {
        "project": project_model_to_schema(project),
        "file": audio_file_model_to_schema(audio_file, public_url),
    }


@router.patch("/{project_id}/files/{file_id}")
async def patch_file(
    project_id: UUID,
    file_id: UUID,
    body: UpdateAudioFileSchema,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Updating file {file_id} for project {project_id}")
    logger.debug(f"Payload: {body.model_dump()}")

    file = await AudioFileRepo.instance.update_file(db, file_id, user.id, body)

    if not file:
        logger.warning(f"Update failed, project {file_id} not found")
        raise api.HTTPException(api.status.HTTP_400_BAD_REQUEST, "File not found")

    public_url = SSSRepo.create_instance().get_public_url(file.file_path_raw)
    EventManager.notify(
        AudioFileEvent.from_table(
            file,
            user.id + str(project_id),
            EventType.file_updated,
            public_url=public_url,
        )
    )

    return audio_file_model_to_schema(file, public_url)


@router.delete("/{project_id}/files/{file_id}")
async def delete_file(
    project_id: UUID,
    file_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    await ProjectRepo.instance.get_project_or_404(db, project_id, user.id)
    did_delete = await AudioFileRepo.instance.delete_file(db, file_id, user.id)

    if not did_delete:
        logger.warning(f"Delete failed, project {project_id} not found")
        raise api.HTTPException(api.status.HTTP_404_NOT_FOUND, "Project not found")

    EventManager.notify(
        AudioFileEvent.no_data(
            user.id + str(project_id),
            EventType.file_deleted,
        )
    )

    return api.responses.JSONResponse(
        status_code=api.status.HTTP_200_OK,
        content={"detail": "File deleted successfully"},
    )
