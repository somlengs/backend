from dataclasses import dataclass, field
from uuid import UUID
from app.entities.types.enums.processing_status import ProcessingStatus


@dataclass
class TaskLog:
    project_id: UUID
    status: ProcessingStatus
    completed_tasks: int
    total_tasks: int
    message: str = field(default='')
    error: int | None = field(default=None)
    task_statuses: dict[UUID, ProcessingStatus] | None = field(default=None)
    stop_connections: bool = False

@dataclass
class SubTaskLog:
    file_id: UUID
    status: ProcessingStatus
    progress: float | None
    message: str = field(default='')
    error: int | None = field(default=None)
    
    def __repr__(self) -> str:
        if self.status != ProcessingStatus.error:
            prog = f'prog={self.progress}. ' if self.progress else ''
            return f'File {self.file_id} status={self.status.name}. {prog}{self.message}'
        else:
            return f'File {self.file_id} errored ({self.error}). {self.message}'
