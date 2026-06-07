from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.config import settings
from app.models.transcription import TranscriptionRecord, TranscriptionStatus


class TranscriptionStore:
    def __init__(self) -> None:
        self._records: dict[str, TranscriptionRecord] = {}
        self._lock = Lock()
        Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    def create(self, youtube_url: str) -> TranscriptionRecord:
        now = datetime.now(timezone.utc)
        record = TranscriptionRecord(
            id=uuid4().hex,
            youtube_url=youtube_url,
            status=TranscriptionStatus.queued,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._records[record.id] = record
        return record

    def get(self, transcription_id: str) -> TranscriptionRecord | None:
        with self._lock:
            return self._records.get(transcription_id)

    def update(
        self,
        transcription_id: str,
        *,
        status: TranscriptionStatus | None = None,
        midi_path: Path | None = None,
        musicxml_path: Path | None = None,
        pdf_path: Path | None = None,
        error: str | None = None,
    ) -> TranscriptionRecord | None:
        with self._lock:
            record = self._records.get(transcription_id)
            if record is None:
                return None
            update_data = {
                "updated_at": datetime.now(timezone.utc),
                "status": status or record.status,
                "midi_path": midi_path or record.midi_path,
                "musicxml_path": musicxml_path or record.musicxml_path,
                "pdf_path": pdf_path or record.pdf_path,
                "error": error,
            }
            updated = record.model_copy(update=update_data)
            self._records[transcription_id] = updated
            return updated


transcription_store = TranscriptionStore()
