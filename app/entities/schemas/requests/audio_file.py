from pydantic import BaseModel


class UpdateAudioFileSchema(BaseModel):
    file_name: str | None
    description: str | None
