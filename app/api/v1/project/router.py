import time
from uuid import UUID

import fastapi as api
from sqlalchemy.orm import Session

from .services import *
from app.core.deps.auth import auth_user
from app.core.deps.db import get_db
from app.core.logger import get
from app.entities import models
from app.entities.dto.responses.project import project_model_to_schema
from app.entities.schemas.auth_user import AuthUser
from app.entities.schemas.params.listing.project import ProjectListingParams
from app.entities.schemas.requests.project import UpdateProjectSchema
from app.entities.types.enums.ordering import Ordering
from app.entities.types.enums.processing_status import ProcessingStatus
from app.entities.types.enums.sorting import ProjectSorting
from app.entities.types.pagination import Paginated
from app.entities.repositories.project.base import ProjectRepo
from app.entities.schemas.project import Project

router = api.APIRouter(prefix='/project')
logger = get()


@router.post('/')
async def new_project(
    files: list[api.UploadFile],
    background: api.BackgroundTasks,
    name: str = api.Form('New Project'),
    description: str | None = api.Form(None),
    user: AuthUser = api.Depends(auth_user),
):
    logger.info('Creating new project request received')
    logger.debug(f'user={user.id} zip_files_count={len(files)} project_name="{name}"')
    t0 = time.perf_counter()

    service = NewProjectService(files, name, description, user)

    try:
        service.validate_data()

        service.create_project_instance()

        await service.upload_project()

        await service.extract_zip()

        num_of_files = len(service.files_to_process)

        background.add_task(service.process_files)
        logger.debug('Background processing task scheduled')

        res = project_model_to_schema(service.project)
        res.num_of_files = num_of_files
        logger.info(f'Empty project {service.project.id} created and returned (took {(time.perf_counter() - t0):.4f}s)')

        return res

    except Exception as exc:
        logger.error(f'Project creation failed: {exc.args[0]}', exc_info=True)
        service.close()
        raise


@router.get('/')
async def get_all(
    page: int = api.Query(1, ge=1),
    limit: int = api.Query(20, ge=1, le=100),
    name: str = api.Query(""),
    status: ProcessingStatus | None = api.Query(None),
    sort: ProjectSorting = api.Query(ProjectSorting.updated_at),
    order: Ordering = api.Query(Ordering.desc),
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
) -> Paginated[Project]:
    logger.info("Fetch project list")
    logger.debug(f"user={user.id} page={page} limit={limit} sort={sort} order={order} status={status}")


    result = await ProjectRepo.instance.get_all_projects_for_user(
        db,
        user.id,
        ProjectListingParams(
            page=page,
            limit=limit,
            project_name=name,
            status=status,
            sort=sort,
            order=order,
        ),
        mapper=project_model_to_schema,
    )

    logger.info(f"Returned {len(result['data'])} projects")
    return {
        "data": result["data"],
        "pagination": result["pagination"]
    }


@router.get('/{project_id}')
async def get_project(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Fetching project {project_id}")
    project = await ProjectRepo.instance.get_project_by_id(db, str(project_id), user.id)

    if not project:
        logger.warning(f"Project {project_id} not found for user {user.id}")
        raise api.HTTPException(api.status.HTTP_404_NOT_FOUND, "Project not found")

    logger.debug(f"Project {project_id} retrieved")
    return project_model_to_schema(project)


@router.patch('/{project_id}')
async def patch(
    project_id: UUID,
    body: UpdateProjectSchema,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Updating project {project_id}")
    logger.debug(f"Payload: {body.model_dump()}")

    project = await ProjectRepo.instance.update_project(
        db, project_id, user.id, body
    )

    if not project:
        logger.warning(f"Update failed, project {project_id} not found")
        raise api.HTTPException(api.status.HTTP_404_NOT_FOUND, "Project not found")

    logger.info(f"Project {project_id} updated")
    return project_model_to_schema(project)


@router.delete('/{project_id}')
async def delete(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Deleting project {project_id}")

    did_delete = await ProjectRepo.instance.delete_project(db, project_id, user.id)
    
    if not did_delete:
        logger.warning(f"Delete failed, project {project_id} not found")
        raise api.HTTPException(api.status.HTTP_404_NOT_FOUND, "Project not found")

    logger.info(f"Project {project_id} deleted")
    return api.responses.JSONResponse(
        status_code=api.status.HTTP_200_OK,
        content={"detail": "Project deleted successfully"},
    )


@router.post('/{project_id}/process')
async def process_project(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Process trigger requested for project {project_id}")

    project = await ProjectRepo.instance.get_project_or_404(db, str(project_id), user.id)

    logger.debug(f"Project {project_id} ready for processing trigger")
    ...


@router.get('/{project_id}/download')
async def download_project(
    project_id: UUID,
    user: AuthUser = api.Depends(auth_user),
    db: Session = api.Depends(get_db),
):
    logger.info(f"Download requested for project {project_id}")

    project = await ProjectRepo.instance.get_project_or_404(db, str(project_id), user.id)
    
    logger.debug(f"Project {project_id} download authorized")
    ...
