# ScoreAI

ScoreAI converts a YouTube link into piano sheet music. This initial scaffold includes a React web client, a FastAPI backend, Docker Compose for local development, and a mocked transcription pipeline with clear extension points for the real audio workflow.

## Stack

- Frontend: React, TypeScript, Vite, Tailwind
- Backend: Python, FastAPI
- Audio pipeline placeholders: yt-dlp, ffmpeg, Basic Pitch, music21, MuseScore CLI
- Local development: Docker Compose

## Project Structure

```text
apps/
  api/
    app/
      jobs/
      models/
      routes/
      services/
  web/
outputs/
```

Generated MIDI, MusicXML, PDF, and temporary audio files belong in `outputs/`.

## Quick Start

1. Copy environment defaults:

```bash
cp .env.example .env
```

2. Start both services:

```bash
docker compose up --build
```

3. Open the app:

```text
http://localhost:5173
```

4. Open the API docs:

```text
http://localhost:8000/docs
```

## API

### `POST /transcriptions`

Starts a transcription job from a YouTube URL.

```json
{
  "youtube_url": "https://www.youtube.com/watch?v=example"
}
```

### `GET /transcriptions/{id}/status`

Returns the current job state and available generated files.

### `GET /transcriptions/{id}/download-midi`

Downloads the generated MIDI file when the job is complete.

### `GET /transcriptions/{id}/download-pdf`

Downloads the generated sheet music PDF when the job is complete.

## Pipeline Notes

The current pipeline is mocked so the app works immediately:

1. Accept a YouTube URL.
2. Create a transcription job.
3. Simulate the pipeline stages.
4. Generate placeholder `.mid`, `.musicxml`, and `.pdf` files.

The real implementation should replace `apps/api/app/services/pipeline.py` with calls to:

- `yt-dlp` to extract audio from YouTube.
- `ffmpeg` to normalize/convert audio.
- Basic Pitch to transcribe audio to MIDI.
- `music21` to process MIDI/MusicXML.
- MuseScore CLI to export polished sheet music PDFs.

The API container installs the minimal runtime dependencies by default. Install optional pipeline dependencies with:

```bash
pip install -r apps/api/requirements-pipeline.txt
```

## Environment Variables

| Name | Default | Description |
| --- | --- | --- |
| `API_HOST` | `0.0.0.0` | FastAPI host used by local/dev containers. |
| `API_PORT` | `8000` | FastAPI port. |
| `OUTPUT_DIR` | `/app/outputs` | Directory for generated files. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed frontend origins. |
| `MOCK_PIPELINE` | `true` | Keep the pipeline mocked until real processing is implemented. |
| `YTDLP_AUDIO_FORMAT` | `bestaudio/best` | Future yt-dlp format selector. |
| `FFMPEG_BIN` | `ffmpeg` | Future ffmpeg binary path. |
| `MUSESCORE_BIN` | `mscore` | Future MuseScore CLI binary path. |
