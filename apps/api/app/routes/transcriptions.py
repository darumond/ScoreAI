from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.jobs.transcription_job import run_transcription_job
from app.models.transcription import (
    TranscriptionCreateRequest,
    TranscriptionCreateResponse,
    TranscriptionStatusResponse,
)
from app.services.storage import transcription_store

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


@router.post("", response_model=TranscriptionCreateResponse, status_code=202)
def create_transcription(
    payload: TranscriptionCreateRequest,
    background_tasks: BackgroundTasks,
) -> TranscriptionCreateResponse:
    record = transcription_store.create(str(payload.youtube_url))
    background_tasks.add_task(run_transcription_job, record.id)
    return TranscriptionCreateResponse(id=record.id, status=record.status)


@router.get("/{transcription_id}/status", response_model=TranscriptionStatusResponse)
def get_transcription_status(transcription_id: str) -> TranscriptionStatusResponse:
    record = transcription_store.get(transcription_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return TranscriptionStatusResponse.from_record(record)


@router.get("/{transcription_id}/download-midi")
def download_midi(transcription_id: str) -> FileResponse:
    record = transcription_store.get(transcription_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    if record.midi_path is None or not record.midi_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file is not ready")
    return FileResponse(
        record.midi_path,
        media_type="audio/midi",
        filename=f"{transcription_id}.mid",
    )


@router.get("/{transcription_id}/download-pdf")
def download_pdf(transcription_id: str) -> FileResponse:
    record = transcription_store.get(transcription_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    if record.pdf_path is None or not record.pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file is not ready")
    return FileResponse(
        record.pdf_path,
        media_type="application/pdf",
        filename=f"{transcription_id}.pdf",
    )
