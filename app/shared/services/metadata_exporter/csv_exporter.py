from io import BytesIO
from typing import Literal
from zipfile import ZipFile, ZIP_DEFLATED

from app.entities.models.audio_file import AudioFileTable
from app.entities.models.project import ProjectTable
from app.entities.repositories.sss.base import SSSRepo
from app.entities.types.enums.processing_status import ProcessingStatus


class CSVExporter:
    def __init__(self, divider: Literal[',', '\t'] = ',', use_headers: bool = False) -> None:
        self.divider = divider
        self.ext = '.tsv' if divider == '\t' else '.csv'
        self.use_headers = use_headers

    def get_metadata(self, project: ProjectTable) -> tuple[str, list[AudioFileTable]]:
        buffer = ''
        if self.use_headers:
            buffer = f'path{self.divider}text\n'
        files = sorted(project.files, key=lambda x: x.file_name)
        exported_files = []

        for file in files:
            if file.transcription_status != ProcessingStatus.completed or not file.transcription_content:
                continue
            *file_names, ext = file.file_name.split('.')
            buffer = buffer + f'{'.'.join(file_names)}{self.divider}{file.transcription_content}\n'
            exported_files.append(file)

        return (buffer, exported_files)

    async def export(self, project: ProjectTable) -> BytesIO:
        buffer = BytesIO()

        metadata, files = self.get_metadata(project)

        with ZipFile(buffer, 'w', ZIP_DEFLATED) as zf:
            for file in files:
                data = await SSSRepo.create_instance().download(file.file_path_raw)
                zf.writestr(f'files/{file.file_name}', data)
                
            zf.writestr(f'metadata{self.ext}', metadata)
            
        buffer.seek(0)
        
        return buffer