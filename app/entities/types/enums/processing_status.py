from enum import StrEnum


class ProcessingStatus(StrEnum):
    draft = 'draft'
    in_progress = 'in_progress'
    completed = 'completed'
    archived = 'archived'
