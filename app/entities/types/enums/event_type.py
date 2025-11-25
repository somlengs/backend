from enum import StrEnum


class EventType(StrEnum):
    project_created = 'project.created'
    project_updated = 'project.updated'
    project_deleted = 'project.deleted'
    file_created = 'file.created'
    file_updated = 'file.updated'
    file_deleted = 'file.deleted'
    other = 'other'