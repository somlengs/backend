from datetime import datetime

from app.entities.models.project import ProjectTable
from app.entities.schemas.events.event import SEvent
from app.entities.types.enums.event_type import EventType
from app.entities.types.enums.processing_status import ProcessingStatus


class ProjectEvent(SEvent):
    project_id: str | None
    """UUID as str"""
    name: str | None
    description: str | None
    status: ProcessingStatus | None
    progress: float | None
    num_of_files: int | None
    created_at: datetime | None
    updated_at: datetime | None
    created_by: str | None
    """User UUID as str"""

    @classmethod
    def from_table(
        cls,
        project: ProjectTable,
        eid: str,
        event_type: EventType,
    ):
        return cls(
            eid=eid,
            event_type=event_type,
            name=project.name,
            project_id=str(project.id),
            description=project.description,
            status=project.status,
            progress=project.progress,
            num_of_files=project.num_of_files,
            created_at=project.created_at,
            updated_at=project.updated_at,
            created_by=str(project.created_by),
        )

    @classmethod
    def no_data(
        cls,
        eid: str,
        event_type: EventType,
    ):
        return cls(
            eid=eid,
            event_type=event_type,
            name=None,
            project_id=None,
            description=None,
            status=None,
            progress=None,
            num_of_files=None,
            created_at=None,
            updated_at=None,
            created_by=None,
        )