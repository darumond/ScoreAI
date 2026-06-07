from pathlib import Path
from time import sleep

from app.config import settings


class TranscriptionPipeline:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_audio(self, transcription_id: str, youtube_url: str) -> Path:
        sleep(0.4)
        audio_path = self.output_dir / f"{transcription_id}.source.txt"
        audio_path.write_text(
            f"Mock audio extracted from {youtube_url}\n"
            f"Future tool: yt-dlp -f {settings.ytdlp_audio_format}\n",
            encoding="utf-8",
        )
        return audio_path

    def convert_audio(self, transcription_id: str, source_path: Path) -> Path:
        sleep(0.4)
        wav_path = self.output_dir / f"{transcription_id}.wav.txt"
        wav_path.write_text(
            f"Mock normalized audio from {source_path.name}\n"
            f"Future tool: {settings.ffmpeg_bin}\n",
            encoding="utf-8",
        )
        return wav_path

    def transcribe_to_midi(self, transcription_id: str, wav_path: Path) -> Path:
        sleep(0.4)
        midi_path = self.output_dir / f"{transcription_id}.mid"
        midi_path.write_bytes(self._mock_midi_bytes(wav_path.name))
        return midi_path

    def generate_musicxml(self, transcription_id: str, midi_path: Path) -> Path:
        sleep(0.4)
        musicxml_path = self.output_dir / f"{transcription_id}.musicxml"
        musicxml_path.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <part-list>
    <score-part id="P1">
      <part-name>Piano</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
""",
            encoding="utf-8",
        )
        return musicxml_path

    def export_pdf(self, transcription_id: str, musicxml_path: Path) -> Path:
        sleep(0.4)
        pdf_path = self.output_dir / f"{transcription_id}.pdf"
        pdf_path.write_bytes(self._mock_pdf_bytes(musicxml_path.name))
        return pdf_path

    @staticmethod
    def _mock_midi_bytes(source_name: str) -> bytes:
        return (
            b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00`"
            b"MTrk\x00\x00\x00\x18"
            b"\x00\xff\x03\x07ScoreAI"
            b"\x00\x90<@"
            b"\x81@\x80<@"
            b"\x00\xff/\x00"
            + f"\nMock source: {source_name}\n".encode("utf-8")
        )

    @staticmethod
    def _mock_pdf_bytes(source_name: str) -> bytes:
        body = f"ScoreAI mock PDF generated from {source_name}"
        return (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R >> endobj\n"
            + f"4 0 obj << /Length {len(body) + 36} >> stream\nBT /F1 18 Tf 72 720 Td ({body}) Tj ET\nendstream endobj\n".encode(
                "utf-8"
            )
            + b"trailer << /Root 1 0 R >>\n%%EOF\n"
        )


pipeline = TranscriptionPipeline(settings.output_dir)
