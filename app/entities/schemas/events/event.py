from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.entities.types.enums.event_type import EventType


def _now_utc() -> datetime:
    return datetime.now(UTC)


class SEvent(BaseModel):
    eid: object
    event_type: EventType
    time: datetime = Field(init=False, default_factory=_now_utc)
