from pydantic import BaseModel


class UpdateProjectSchema(BaseModel):
    name: str | None
    description: str | None
