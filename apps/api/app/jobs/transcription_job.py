from app.models.transcription import TranscriptionStatus
from app.services.pipeline import pipeline
from app.services.storage import transcription_store


def run_transcription_job(transcription_id: str) -> None:
    record = transcription_store.get(transcription_id)
    if record is None:
        return

    try:
        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.extracting_audio,
        )
        source_path = pipeline.extract_audio(transcription_id, record.youtube_url)

        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.converting_audio,
        )
        wav_path = pipeline.convert_audio(transcription_id, source_path)

        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.transcribing_midi,
        )
        midi_path = pipeline.transcribe_to_midi(transcription_id, wav_path)

        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.generating_score,
            midi_path=midi_path,
        )
        musicxml_path = pipeline.generate_musicxml(transcription_id, midi_path)

        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.exporting_pdf,
            musicxml_path=musicxml_path,
        )
        pdf_path = pipeline.export_pdf(transcription_id, musicxml_path)

        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.completed,
            midi_path=midi_path,
            musicxml_path=musicxml_path,
            pdf_path=pdf_path,
        )
    except Exception as exc:
        transcription_store.update(
            transcription_id,
            status=TranscriptionStatus.failed,
            error=str(exc),
        )
