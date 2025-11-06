from enum import StrEnum

from sqlalchemy import Column

from app.entities.models.project import ProjectTable


class ProjectSorting(StrEnum):
    project_name = 'project_name'
    status = 'status'
    progress = 'progress'
    created_at = 'created_at'
    updated_at = 'updated_at'
    
    def column(self) -> Column[ProjectTable]:
        mapping = {
            ProjectSorting.project_name: ProjectTable.name,
            ProjectSorting.status: ProjectTable.status,
            ProjectSorting.progress: ProjectTable.progress,
            ProjectSorting.created_at: ProjectTable.created_at,
            ProjectSorting.updated_at: ProjectTable.updated_at,
        }
        return mapping[self]


class AudioFileSorting(StrEnum):
    file_name = 'file_name'
    status = 'status'
    progress = 'progress'
    created_at = 'created_at'
    updated_at = 'updated_at'
    file_size = 'file_size'
    duration = 'duration'
    file_format = 'file_format'
