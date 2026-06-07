from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, HttpUrl


class TranscriptionStatus(StrEnum):
    queued = "queued"
    extracting_audio = "extracting_audio"
    converting_audio = "converting_audio"
    transcribing_midi = "transcribing_midi"
    generating_score = "generating_score"
    exporting_pdf = "exporting_pdf"
    completed = "completed"
    failed = "failed"


class TranscriptionCreateRequest(BaseModel):
    youtube_url: HttpUrl


class TranscriptionCreateResponse(BaseModel):
    id: str
    status: TranscriptionStatus


class TranscriptionRecord(BaseModel):
    id: str
    youtube_url: str
    status: TranscriptionStatus
    created_at: datetime
    updated_at: datetime
    midi_path: Path | None = None
    musicxml_path: Path | None = None
    pdf_path: Path | None = None
    error: str | None = None


class TranscriptionStatusResponse(BaseModel):
    id: str
    youtube_url: str
    status: TranscriptionStatus
    created_at: datetime
    updated_at: datetime
    has_midi: bool
    has_pdf: bool
    error: str | None = None

    @classmethod
    def from_record(cls, record: TranscriptionRecord) -> "TranscriptionStatusResponse":
        return cls(
            id=record.id,
            youtube_url=record.youtube_url,
            status=record.status,
            created_at=record.created_at,
            updated_at=record.updated_at,
            has_midi=record.midi_path is not None and record.midi_path.exists(),
            has_pdf=record.pdf_path is not None and record.pdf_path.exists(),
            error=record.error,
        )
