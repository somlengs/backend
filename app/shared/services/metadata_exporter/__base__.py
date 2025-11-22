from io import BytesIO
from typing import Protocol
from zipfile import ZipFile

from app.entities.models.project import ProjectTable

class Exporter(Protocol):
    async def export(self, project: ProjectTable) -> BytesIO:
        ...