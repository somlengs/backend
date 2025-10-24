from app.entities.dto.responses.audio_file import audio_file_model_to_schema
from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.schemas.responses.project import ProjectListingResponse


def project_model_to_schema(project: ProjectTable) -> ProjectListingResponse:
    return ProjectListingResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        progress=project.progress,
        project_path=project.project_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        files=[audio_file_model_to_schema(f) for f in project.files]
    )
