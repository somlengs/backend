from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.entities.models.project import ProjectTable

class UpdateProjectSchema(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None

    def update(self, project: ProjectTable):
        if self.name is not None:
            project.name = self.name

        if self.description is not None:
            if self.description:
                project.description = self.description
            else:
                project.description = None
                
        project.updated_at = datetime.now(UTC)
