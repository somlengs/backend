from __future__ import annotations

from enum import StrEnum


class ProcessingStatus(StrEnum):
    loading = "loading"
    pending = "pending"
    processing = "processing"
    completed = "completed"
    error = "error"

    @classmethod
    def from_str(cls, value: str) -> ProcessingStatus:
        try:
            return cls(value)
        except ValueError as e:
            raise ValueError(f"Invalid status: {value!r}") from e
