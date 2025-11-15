from pydantic import BaseModel


class TranscriptionResult(BaseModel):
    status_code: int
    transcription: str
    audio_filename: str
    model_used: str